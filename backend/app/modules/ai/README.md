# AI Module

AI-powered features for Gear Stack using OpenRouter API.

## Overview

This module provides AI functionality including:
- Chat interface with structured JSON output
- Automatic database updates from AI responses
- Analysis and optimization suggestions
- Pack generation
- History tracking and cost monitoring

**Access:** Admin users only (initial release)

## Structure

```
ai/
├── routers/          # API endpoints (split by resource)
├── services/         # Business logic (split by feature)
├── repositories/     # Database operations
├── schemas/          # Pydantic request/response schemas
├── providers/        # OpenRouter integration
├── cache/            # PostgreSQL cache implementation
├── prompts/          # AI prompt templates
├── parsers/          # Response parsing logic
└── utils/            # Helper functions
```

## Key Features

### 1. Chat with Structured Output
- User sends natural language request
- AI returns JSON with structured data
- System automatically applies updates to database
- Supports: update_items, create_items, update_container, create_container

### 2. History Tracking
- All interactions saved to database
- Full context preserved (prompt, response, tokens, cost)
- Browsable history with filters

### 3. Token Management
- User tokens encrypted at rest (Fernet)
- Token validation on save
- Cost and usage tracking

### 4. Cache System
- PostgreSQL-based cache for repeated operations
- 7-day TTL for classifications
- Reduces API costs

## Configuration

Required environment variables:

```bash
# OpenRouter API (system token for admins without own token)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Token encryption key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
AI_TOKEN_ENCRYPTION_KEY=...

# Cache settings
AI_CACHE_ENABLED=true
AI_CACHE_TTL_CLASSIFY=7  # days
```

## Usage

### Adding to Main Router

```python
# In backend/app/main.py or router registration
from app.modules.ai import router as ai_router

app.include_router(ai_router, prefix="/api")
```

### Admin Middleware

All AI endpoints are protected with `require_admin` dependency:

```python
from app.modules.ai.dependencies import require_admin

@router.post("/chat")
async def chat(
    request: ChatRequest,
    admin_user: CurrentUser = Depends(require_admin)
):
    ...
```

## Development

### Running Tests

```bash
# Run all AI module tests
pytest backend/tests/modules/ai/

# Run specific test file
pytest backend/tests/modules/ai/test_chat_service.py

# Run with coverage
pytest backend/tests/modules/ai/ --cov=app.modules.ai
```

### Adding New Features

1. Create service in `/services/`
2. Add schemas in `/schemas/`
3. Create router in `/routers/`
4. Register router in main `router.py`
5. Add tests in `backend/tests/modules/ai/`

## API Endpoints

- `POST /api/ai/chat` - Main chat endpoint
- `GET /api/ai/models` - List available models
- `GET /api/ai/settings` - Get user AI settings
- `PUT /api/ai/settings` - Update AI settings
- `POST /api/ai/settings/token` - Add/validate token
- `DELETE /api/ai/settings/token` - Remove token
- `GET /api/ai/history` - Get history list
- `GET /api/ai/history/:id` - Get history detail
- `DELETE /api/ai/history/:id` - Delete history item
- `DELETE /api/ai/history` - Clear all history

## Security

- All endpoints require authentication
- Admin-only access via `require_admin` middleware
- Tokens encrypted at rest using Fernet
- No token exposure in logs or responses
- Input validation on all requests

## Contributing

See [FEATURE-AI-IMPLEMENTATION.md](../../../docs/features/FEATURE-AI-IMPLEMENTATION.md) for detailed implementation plan.
