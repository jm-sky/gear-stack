# Item image endpoints — broken object-level authorization (IDOR)

**Status:** `verification needed`
**Created:** 2026-07-21
**Severity:** High
**Module:** `gear` (backend — item images)
**Source:** [Security review — Backend](../reviews/2026-07-06-security-backend.md) (SEC-BE-01)

## Problem

The item-image endpoints in [`backend/app/modules/gear/item_image_router.py`](../../backend/app/modules/gear/item_image_router.py) enforce a *role* (`PremiumOrHigherUser`) but never verify that the target **item** or **image** belongs to the caller. Because the role is shared by every premium/admin/owner user, any such user can act on any other user's item images by ID. One endpoint has no authentication at all.

Confirmed by tracing the service and repository:

- [`image_upload_service.py`](../../backend/app/modules/gear/image_upload_service.py):
  - `delete_image(image_id, user_id)` — fetches the image by ID and deletes it; the `user_id` argument is documented as "for authorization check" but is **never compared** to `image.user_id`.
  - `reorder_images(item_id, ...)`, `toggle_primary_image(item_id, image_id)`, `upload_image(...)` — operate purely by `item_id`/`image_id`, no ownership check.
  - `_process_and_store_image` stores the uploaded image against any `item_id` the caller supplies (no check that the item is theirs).
- [`item_image_repository.py`](../../backend/app/modules/gear/item_image_repository.py): `get_by_id`, `get_by_item`, `delete`, `update`, `unset_primary_for_item` all key on `item_id`/`image_id` with **no join to the owning user**.

## Impact

Assuming ≥2 users hold the premium (or admin/owner) role — the intended audience for this feature:

- **Cross-user image deletion:** `DELETE /api/items/images/{image_id}` removes any user's image.
- **Cross-user tampering:** `PUT /api/items/{item_id}/images/reorder` and `.../{image_id}/primary` mutate any user's item images.
- **Cross-user write:** `POST /api/items/{item_id}/images` (and `/from-url`) attach images to another user's item.
- **Unauthenticated read:** `GET /api/items/{item_id}/images` has **no auth dependency at all** — anyone can enumerate any item's images (URLs, filenames, sizes) by guessing/scraping item IDs.

Note the sibling **catalogue** image router ([`catalogue_item_image_router.py`](../../backend/app/modules/gear/catalogue_item_image_router.py)) is correctly scoped to `AdminOrOwnerUser` (a shared admin-managed resource), so no ownership check is needed there — this issue is specific to per-user *item* images.

## Reproduction (sketch)

1. Users A and B both have the premium role.
2. B uploads an image to their item → note `image_id` from the response.
3. A calls `DELETE /api/items/images/{image_id}` with A's token → 200, B's image is gone.
4. Anonymous client calls `GET /api/items/{B_item_id}/images` → 200 with B's image metadata.

## Proposed fix

- Add an ownership guard in `ImageUploadService`:
  - For item-scoped operations, verify the `item_id` belongs to `user_id` (join `ItemImageDB`/gear item → container `user_id`, mirroring `GearRepository.get_item(item_id, user_id)` at [`repository.py:423`](../../backend/app/modules/gear/repository.py)).
  - For image-scoped operations (`delete_image`, `toggle_primary_image`), load the image and assert `image.user_id == user_id` (or the item→owner join) before mutating; return 404 (not 403) on mismatch to avoid ID enumeration.
- Add auth + ownership to `get_item_images` (currently unauthenticated). If item images are meant to be public for public containers, scope the read to items belonging to a *public* container; otherwise require the owner.
- Prefer enforcing this in the repository query (`WHERE user_id = :user_id`) so a missing check fails closed.

## Scope

- [x] `backend/app/modules/gear/image_upload_service.py` — ownership checks in `upload_image`, `delete_image`, `reorder_images`, `toggle_primary_image`, `get_item_images`, `upload_image_from_url`, `validate_upload`
- [x] `backend/app/modules/gear/item_image_router.py` — added optional-auth to `get_item_images`; owner-or-public-container read policy
- [x] `backend/app/modules/gear/item_image_repository.py` — owner-scoped query variants (`get_item_owner_and_visibility`, `get_item_owner_id`, `get_image_owner_id`, `image_belongs_to_item`)
- [x] Integration tests: user A cannot read/modify/delete user B's item images; unauthenticated read is rejected for private containers, allowed for public ones (`backend/tests/integration/gear/test_item_images_authorization.py`)

## Resolution (2026-07-22)

Went with **"public for public containers"** (confirmed with the user): images are visible without auth only when `item.container.is_public` and not hidden by reports; every mutation endpoint (upload, delete, reorder, toggle-primary, upload-from-url) requires strict ownership, resolved by joining `ItemImageDB → GearItemDB → GearContainerDB.user_id` (mirrors `GearRepository.get_item`). Mismatches return 404, not 403, to avoid ID enumeration.

Also closed two adjacent IDOR gaps found while fixing this: `reorder_images` and `toggle_primary_image` previously trusted `image_id` without checking it actually belongs to `item_id` — a caller who owned *some* item could reorder/toggle images belonging to a different item (their own or, combined with the missing ownership check, anyone's).

`get_optional_user`/`OptionalUser` was extracted from `gear/router.py` into a new `gear/dependencies.py` so `item_image_router.py` (included by `router.py`) could use it without a circular import.

Automated tests cover all "Verification" scenarios below at the service layer (real Postgres via the existing integration-test fixtures). Marked `verification needed` rather than `done` pending a manual click-through against the running app (no live manual pass was done this session).

## Verification

1. Two premium users; confirm each of the five operations above returns 404/403 across users. — covered by `test_item_images_authorization.py`.
2. `GET /api/items/{item_id}/images` unauthenticated → 404 for a private container, 200 for a public one. — covered.
3. Owner still succeeds on their own items/images. — covered.
