import { test } from '@playwright/test'
import { readFileSync, writeFileSync } from 'fs'
import { join } from 'path'
import * as readline from 'readline'
import type { CatalogueItem } from '../backend/app/seeders/catalogue_items.types'

/**
 * Category keywords for matching products
 * Used to verify if search results match the product category
 */
const CATEGORY_KEYWORDS: Record<string, string[]> = {
  fire: ['zapalniczka', 'lighter', 'zapałki', 'matches', 'krzesiwo', 'flint', 'fire', 'ogień', 'torch', 'pochodnia'],
  water: ['butelka', 'bottle', 'woda', 'water', 'bidon', 'canteen', 'filt', 'filter'],
  food: ['jedzenie', 'food', 'racja', 'ration', 'menażka', 'mess', 'kubek', 'cup'],
  shelter: ['namiot', 'tent', 'tarp', 'plachta', 'śpiwór', 'sleeping', 'bag', 'hamak', 'hammock'],
  light: ['latarka', 'flashlight', 'czołówka', 'headlamp', 'baterie', 'batteries'],
  tools: ['nóż', 'knife', 'multitool', 'multitools', 'scyzoryk', 'siekiera', 'axe', 'piła', 'saw', 'kompas', 'compass', 'tool', 'tools', 'shovel', 'saperka', 'łopata'],
  firstAid: ['apteczka', 'first', 'aid', 'bandaż', 'bandage', 'plaster', 'gazik'],
  navigation: ['kompas', 'compass', 'mapa', 'map', 'gps', 'lornetka', 'binoculars'],
  communication: ['radio', 'telefon', 'phone', 'powerbank', 'ładowarka', 'charger'],
  other: [],
}


interface ProductLink {
  url: string
  price?: number
  variant?: string
}

interface SearchResult {
  productId: string
  productName: string
  foundUrls: ProductLink[]
}

/**
 * Load products from JSON file
 */
function loadProductsFromJson(jsonPath: string): CatalogueItem[] {
  const content = readFileSync(jsonPath, 'utf-8')
  return JSON.parse(content) as CatalogueItem[]
}

/**
 * Generate search query for a product
 */
function generateSearchQuery(product: CatalogueItem): string {
  // Try brand + model first (only if brand is not Generic)
  if (product.brand && product.brand !== 'Generic' && product.brand !== 'Generic / MIL-SPEC') {
    if (product.model && product.model.trim()) {
      const query = `${product.brand} ${product.model}`.trim()
      if (query) return query
    }
    // If model is missing/empty, try just brand
    if (product.brand.trim()) return product.brand.trim()
  }

  // Fallback to product name
  if (product.name && product.name.trim()) {
    return product.name.trim()
  }

  // Last resort: use brand or model if available
  if (product.brand && product.brand.trim()) return product.brand.trim()
  if (product.model && product.model.trim()) return product.model.trim()

  // Should never happen, but return empty string as fallback
  console.warn(`Warning: No search query could be generated for product ${product.id}`)
  return ''
}

/**
 * Update catalogue_items.json with found URLs
 */
function updateJsonFile(jsonPath: string, results: SearchResult[]): void {
  try {
    const products = JSON.parse(readFileSync(jsonPath, 'utf-8')) as CatalogueItem[]

    let updatedCount = 0
    for (const result of results) {
      const product = products.find(p => p.id === result.productId)
      if (product) {
        if (result.foundUrls.length === 0) {
          // Mark product as processed by setting empty shops array
          // This prevents reprocessing the same product
          product.shops = []
          updatedCount++
        } else {
          // Map ProductLink to shop format with price and variant
          product.shops = result.foundUrls.map(productLink => {
            const shop: { url: string; variant?: string; price?: number; currency?: string } = {
              url: productLink.url
            }
            if (productLink.variant) {
              shop.variant = productLink.variant
            }
            if (productLink.price) {
              shop.price = productLink.price
              shop.currency = 'PLN'
            }
            return shop
          })
          updatedCount++
        }
      }
    }

    writeFileSync(jsonPath, JSON.stringify(products, null, 2), 'utf-8')
    console.log(`Updated ${updatedCount} products in JSON file`)
  } catch (error) {
    console.error('Error updating JSON file:', error)
  }
}


test.describe('Find products on militaria.pl', () => {
  test('Search and collect product URLs', async ({ page }) => {
    const jsonPath = join(process.cwd(), 'backend/app/seeders/catalogue_items.json')

    // STEP-BY-STEP MODE: Set to true for interactive debugging
    const STEP_BY_STEP = process.env.STEP_BY_STEP === 'true' || process.env.STEP_BY_STEP === '1'
    const MAX_PRODUCTS = process.env.MAX_PRODUCTS ? parseInt(process.env.MAX_PRODUCTS, 10) : (STEP_BY_STEP ? 1 : undefined)
    const INTERACTIVE = process.env.INTERACTIVE === 'true' || process.env.INTERACTIVE === '1'

    // Create readline interface for interactive mode
    let rl: readline.Interface | null = null
    if (INTERACTIVE) {
      rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
      })
    }

    const allProducts = loadProductsFromJson(jsonPath)
    // Filter products that need shop URLs:
    // - products without shops property (undefined/null) → need processing
    // - products with empty shops array [] → need processing (may have been processed incorrectly)
    // - products with shops array containing items → already processed, has results → skip
    let products = allProducts.filter(p => {
      if (!p.shops) return true // undefined or null → needs processing
      if (Array.isArray(p.shops) && p.shops.length === 0) return true // empty array → needs processing
      if (Array.isArray(p.shops) && p.shops.length > 0) return false // has shops → already processed, skip
      return true // fallback: process if unsure
    })

    if (MAX_PRODUCTS) {
      products = products.slice(0, MAX_PRODUCTS)
      console.log(`🧪 STEP-BY-STEP MODE: Processing only ${products.length} product(s)`)
      if (products.length > 0) {
        console.log(`   Product to process: ${products[0].name} (${products[0].id})`)
      }
    } else {
      console.log(`Found ${products.length} products needing shop URLs`)
    }

    const results: SearchResult[] = []

    for (let idx = 0; idx < products.length; idx++) {
      const product = products[idx]

      if (INTERACTIVE && idx > 0) {
        console.log('\n⏸️  Press Enter to continue to next product...')
        await new Promise<void>(resolve => {
          if (rl) {
            rl.question('', () => {
              resolve()
            })
          } else {
            setTimeout(resolve, 5000) // Fallback timeout
          }
        })
      } else if (STEP_BY_STEP && idx > 0) {
        console.log('\n⏸️  Waiting 5 seconds before next product...')
        await new Promise(resolve => setTimeout(resolve, 5000))
      }

      console.log(`\n${'='.repeat(80)}`)
      console.log(`Product ${idx + 1}/${products.length}: ${product.name}`)
      console.log(`${'='.repeat(80)}`)
      const searchQuery = generateSearchQuery(product)

      // Skip if query is empty
      if (!searchQuery || searchQuery.trim() === '') {
        console.warn(`\n⚠️  Skipping ${product.name} - empty search query`)
        results.push({
          productId: product.id,
          productName: product.name,
          foundUrls: []
        })
        continue
      }

      const encodedQuery = encodeURIComponent(searchQuery)
      // Use pref_q parameter instead of q (as per site structure)
      const searchUrl = `https://militaria.pl/szukaj?pref_q=${encodedQuery}`

      console.log('\n🔍 Step 1: Generating search query')
      console.log(`   Product: ${product.name}`)
      console.log(`   Brand: ${product.brand || 'N/A'}`)
      console.log(`   Model: ${product.model || 'N/A'}`)
      console.log(`   Query: "${searchQuery}" (length: ${searchQuery.length})`)
      console.log(`   URL: ${searchUrl}`)

      // Debug: verify query is not empty
      if (!searchQuery || searchQuery.trim() === '') {
        console.error(`  ❌ ERROR: Empty search query for ${product.name}!`)
        console.error(`  Product data: name="${product.name}", brand="${product.brand}", model="${product.model}"`)
      }

      if (INTERACTIVE) {
        console.log('\n⏸️  Press Enter to navigate to search page...')
        await new Promise<void>(resolve => {
          if (rl) {
            rl.question('', () => {
              resolve()
            })
          } else {
            setTimeout(resolve, 3000) // Fallback timeout
          }
        })
      } else if (STEP_BY_STEP) {
        console.log('\n⏸️  Waiting 3 seconds before navigation...')
        await new Promise(resolve => setTimeout(resolve, 3000))
      }

      try {
        console.log('\n🌐 Step 2: Navigating to search page')
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 })
        console.log(`   ✅ Page loaded: ${page.url()}`)

        // Handle cookie consent (Cookiebot) - only if not already accepted
        console.log('\n🍪 Step 3: Handling cookie consent')
        let cookieClicked = false
        try {
          // Check if cookie consent was already accepted (check for Cookiebot cookie or dialog absence)
          const cookieAlreadyAccepted = await page.evaluate(() => {
            // Check if Cookiebot cookie exists (indicates consent was given)
            return document.cookie.includes('Cookiebot') || 
                   document.cookie.includes('cookiebot') ||
                   // Check if dialog is already hidden/not present
                   !document.querySelector('#CybotCookiebotDialog')
          })

          if (cookieAlreadyAccepted) {
            console.log('   ℹ️  Cookie consent already accepted, skipping')
          } else {
            // Wait briefly for cookie consent dialog to appear (it loads asynchronously)
            console.log('   ⏳ Checking for cookie consent dialog...')
            
            const cookieSelectors = [
              '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
              '#CybotCookiebotDialogBodyButtonAccept',
              'button[id*="CybotCookiebotDialog"][id*="Allow"]',
              'button[id*="CybotCookiebotDialog"][id*="Accept"]',
              '[id*="cookiebot"] button[id*="allow"]',
              '[id*="cookiebot"] button[id*="accept"]',
              'button:has-text("Accept all")',
              'button:has-text("Akceptuj wszystkie")',
              'button:has-text("Allow all")',
            ]

            // Try to find cookie button with short timeout (dialog appears quickly if it will appear)
            for (const selector of cookieSelectors) {
              try {
                // Wait for selector to appear (with short timeout - if it doesn't appear quickly, it won't appear)
                const cookieButton = await page.waitForSelector(selector, {
                  state: 'visible',
                  timeout: 1000 // Reduced from 3000ms - if dialog doesn't appear in 1s, it's probably not coming
                }).catch(() => null)

                if (cookieButton) {
                  await cookieButton.click()
                  console.log('   ✅ Clicked cookie consent')
                  cookieClicked = true
                  // Wait for dialog to disappear
                  await page.waitForSelector(selector, { state: 'hidden', timeout: 2000 }).catch(() => {})
                  break
                }
              } catch {
                // Try next selector
              }
            }
            
            if (!cookieClicked) {
              console.log('   ℹ️  No cookie consent dialog found (already accepted or not needed)')
            }
          }

          // Small delay after cookie handling
          if (cookieClicked) {
            await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {})
            console.log('   ✅ Cookie consent handled')
          } else {
            console.log('   ℹ️  No cookie consent dialog found')
          }
        } catch {
          // Cookie consent not found or already accepted, continue
          console.log('   ℹ️  Cookie consent handling skipped')
        }

        // Wait for search results container to appear (prefixbox structure)
        console.log('\n🔎 Step 4: Waiting for search results')
        let productLinks: Array<{ url: string; price?: number; variant?: string }> = []
        try {
          // Wait for prefixbox results container or any product elements (longer timeout)
          try {
            await page.waitForSelector('#prefixbox-results, li[data-product-id], .prefixbox-product-container-wrapper', { timeout: 25000 })
            console.log('   ✅ Results container found')
          } catch {
            console.log('   ⚠️  Results container not found, trying fallback selectors...')
            // Try waiting for any product links
            const found = await page.waitForSelector('a[href*="/p/"]', { timeout: 10000 }).catch(() => null)
            if (found) {
              console.log('   ✅ Fallback selector found products')
            } else {
              console.log('   ⚠️  No products found with fallback selectors')
            }
          }

          // Additional wait for products to render (shorter wait for async loading)
          console.log('   ⏳ Waiting for async content to load...')
          await page.waitForTimeout(1500) // Reduced from 4000ms to 1500ms
          await page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {}) // Changed from networkidle to domcontentloaded, shorter timeout
          console.log('   ✅ Content loaded')

          // Look for product links in prefixbox structure with price and variant extraction
          productLinks = await page.evaluate(() => {
            const results: Array<{ url: string; price?: number; variant?: string }> = []

            // Find prefixbox results container or use body as fallback
            let resultsContainer = document.querySelector('#prefixbox-results')
            if (!resultsContainer) {
              // Try to find any product container
              resultsContainer = document.querySelector('.prefixbox-products-container') || document.body
              console.log('  [DEBUG] Using fallback container')
            }

            // Try multiple selectors to find product links
            const selectors = [
              '.prefixbox-product-container-wrapper a.product-item-link',
              '.prefixbox-product-container-wrapper a.product.photo.product-item-photo',
              'li[data-product-id] a.product-item-link',
              'li[data-product-id] a.product.photo',
              '#prefixbox-results a[href*="/p/"]',
              'main a[href*="/p/"]' // Fallback to main container
            ]

            const foundUrls = new Set<string>()

            for (const selector of selectors) {
              const links = resultsContainer.querySelectorAll<HTMLAnchorElement>(selector)
              if (links.length > 0) {
                console.log(`  [DEBUG] Found ${links.length} links with selector: ${selector}`)

                links.forEach(link => {
                  const href = link.href
                  // Only include product URLs (containing /p/) and exclude search/category pages
                  if (href && href.includes('/p/') && !href.includes('/szukaj') && !href.includes('/kategoria')) {
                    if (!foundUrls.has(href)) {
                      foundUrls.add(href)

                      // Extract price from product card (in PLN)
                      let price: number | undefined
                      const productCard = link.closest('li[data-product-id]') || link.closest('.prefixbox-product-container-wrapper')
                      if (productCard) {
                        // Look for price element - prefer PLN price container
                        const plnPriceContainer = productCard.querySelector('.pfbx-price-container.pln')
                        const priceElement = plnPriceContainer?.querySelector('.price, .price-wrapper, [data-price-amount]') ||
                                          productCard.querySelector('.price, .price-wrapper, [data-price-amount]')

                        if (priceElement) {
                          const priceText = priceElement.textContent || ''
                          const priceAttr = priceElement.getAttribute('data-price-amount')

                          // Try data-price-amount first (most reliable)
                          if (priceAttr) {
                            // Format: "99,95" or "99.95"
                            const normalized = priceAttr.replace(',', '.')
                            price = parseFloat(normalized)
                          } else {
                            // Parse from text (e.g., "99,95 zł" -> 99.95)
                            // Match: digits, optional comma/dot, optional digits, optional currency
                            const priceMatch = priceText.match(/(\d+)[,\s\.](\d{2})/)
                            if (priceMatch) {
                              const whole = priceMatch[1]
                              const decimal = priceMatch[2]
                              price = parseFloat(`${whole}.${decimal}`)
                            } else {
                              // Try simple number match
                              const simpleMatch = priceText.match(/(\d+)/)
                              if (simpleMatch) {
                                price = parseFloat(simpleMatch[1])
                              }
                            }
                          }
                        }
                      }

                      // Extract variant from product name/link text
                      // Variant is extracted if product name ends with "- Color" pattern
                      let variant: string | undefined
                      const linkText = link.textContent?.trim() || ''
                      const hrefSlug = href.split('/p/').pop()?.split('?')[0] || ''

                      // Color tokens to match (Olive, Black, Green, Khaki, Coyote)
                      const colorTokens = ['olive', 'black', 'green', 'khaki', 'coyote', 'red', 'blue', 'tan', 'brown', 'grey', 'gray', 'white', 'orange', 'midnight', 'od-green', 'polar-white', 'nordic-noir', 'silver', 'gold']

                      // Check if product name ends with "- Color" pattern
                      const nameMatch = linkText.match(/\s*-\s*([^-]+)$/i)
                      if (nameMatch) {
                        const potentialVariant = nameMatch[1].trim().toLowerCase()
                        // Check if it matches any color token
                        for (const color of colorTokens) {
                          if (potentialVariant === color || potentialVariant.includes(color) || color.includes(potentialVariant)) {
                            // Capitalize first letter of each word
                            variant = color.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
                            break
                          }
                        }
                      }

                      // Fallback: check last part of slug
                      if (!variant) {
                        const slugParts = hrefSlug.split('-')
                        const lastPart = slugParts[slugParts.length - 1]?.toLowerCase()
                        for (const color of colorTokens) {
                          if (lastPart === color || lastPart?.includes(color)) {
                            variant = color.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
                            break
                          }
                        }
                      }

                      results.push({ url: href, price, variant })
                    }
                  }
                })

                if (results.length >= 5) break // Stop if we found enough links
              }
            }

            console.log(`  [DEBUG] Total unique URLs found: ${results.length}`)
            return results.slice(0, 5) // Get first 5 unique results
          })

          console.log(`\n📦 Step 5: Extracted ${productLinks.length} product link(s)`)
          if (productLinks.length > 0) {
            productLinks.forEach((link, i) => {
              const priceInfo = link.price ? ` (${link.price} PLN)` : ''
              const variantInfo = link.variant ? ` [${link.variant}]` : ''
              console.log(`   ${i + 1}. ${link.url}${priceInfo}${variantInfo}`)
            })
          }
        } catch (error) {
          console.log(`\n❌ Error finding products: ${error}`)
          // No products found, continue with empty array
          productLinks = []
        }

        // Filter and score URLs to find best matches
        if (productLinks.length > 0) {
          console.log('\n🎯 Step 6: Filtering and scoring URLs')
          console.log(`   Found ${productLinks.length} URLs before filtering`)

          const searchQueryLower = searchQuery.toLowerCase()
          const productNameWords = product.name.toLowerCase().split(' ').filter(w => w.length > 3)
          const brandLower = product.brand?.toLowerCase() ?? ''
          const modelLower = product.model?.toLowerCase() ?? ''

          // Keywords that indicate replacement parts or accessories (exclude these)
          const excludeKeywords = [
            'wymienne', 'replacement', 'parts', 'part', 'akcesoria', 'accessories',
            'przecinaki', 'blade', 'blades', 'noze', 'knife', 'knives',
            'osprzet', 'equipment', 'zestaw-czesci', 'parts-kit'
          ]

          // Category-specific keywords for matching
          const categoryKeywords = CATEGORY_KEYWORDS[product.category] || []
          // const categoryLower = product.category.toLowerCase()

          // Score and filter URLs
          const scoredLinks = productLinks.map(productLink => {
            const url = productLink.url
            const urlLower = url.toLowerCase()
            const urlSlug = url.split('/p/').pop()?.split('?')[0] ?? ''

            // Exclude replacement parts and accessories
            const isReplacementPart = excludeKeywords.some(keyword => urlLower.includes(keyword))
            if (isReplacementPart) {
              return { productLink, score: -1, reason: 'replacement part/accessory' }
            }

            let score = 0

            // CRITICAL: Check if URL matches product category (highest priority check)
            const categoryMatch = categoryKeywords.some(keyword => urlLower.includes(keyword))
            if (!categoryMatch && categoryKeywords.length > 0) {
              // Strong penalty if category keywords don't match
              score -= 20
              console.log(`    ⚠️  Category mismatch: looking for "${product.category}" but URL doesn't contain category keywords`)
            } else if (categoryMatch) {
              // Strong bonus for category match
              score += 15
            }

            // Score based on brand match (high priority)
            if (brandLower && brandLower !== 'generic' && brandLower !== 'generic / mil-spec') {
              if (urlLower.includes(brandLower)) {
                score += 10
                // Bonus if brand appears early in URL
                if (urlSlug.startsWith(brandLower.split(' ')[0])) {
                  score += 5
                }
              } else {
                // Penalty if brand doesn't match (but only if brand is specific)
                score -= 5
              }
            }

            // Score based on model match (high priority, but penalize generic words)
            if (modelLower && modelLower.length > 3) {
              const modelWords = modelLower.split(' ').filter(w => w.length > 2)
              // Penalize generic model words like "classic", "standard", "basic"
              const genericModelWords = ['classic', 'standard', 'basic', 'regular', 'normal', 'simple']
              const isGenericModel = genericModelWords.some(gw => modelLower.includes(gw))

              // Check for exact model match in URL (highest priority for model)
              const exactModelMatch = urlLower.includes(modelLower)
              if (exactModelMatch) {
                score += 30 // Big bonus for exact model match
                // Extra bonus if model appears as a complete word in slug
                const modelInSlug = urlSlug.includes(modelLower) || urlSlug.includes(modelLower.replace(/\s+/g, '-'))
                if (modelInSlug) {
                  score += 20 // Even bigger bonus if model is in slug
                }
              }

              if (isGenericModel) {
                // Only give small score for generic model words
                const modelMatches = modelWords.filter(word => urlLower.includes(word) && !genericModelWords.includes(word)).length
                score += modelMatches * 2
                // Penalty if only generic words match
                if (modelWords.every(word => genericModelWords.includes(word))) {
                  score -= 10
                }
              } else {
                // Normal scoring for specific model words (but less if exact match already scored)
                if (!exactModelMatch) {
                  const modelMatches = modelWords.filter(word => urlLower.includes(word)).length
                  score += modelMatches * 8 // Increased from 5 to 8
                } else {
                  // Partial matches still get some points
                  const modelMatches = modelWords.filter(word => urlLower.includes(word)).length
                  score += modelMatches * 2
                }
              }
            }

            // Score based on product name words (excluding generic words)
            const genericNameWords = ['classic', 'standard', 'basic', 'regular', 'normal', 'simple', 'black', 'green', 'red', 'blue', 'olive', 'tan', 'brown']
            const specificNameWords = productNameWords.filter(w => !genericNameWords.includes(w))
            const nameMatches = specificNameWords.filter(word => urlLower.includes(word)).length
            score += nameMatches * 4

            // Score based on query words (excluding generic words)
            const queryWords = searchQueryLower.split(' ').filter(w => w.length > 3 && !genericNameWords.includes(w))
            const queryMatches = queryWords.filter(word => urlLower.includes(word)).length
            score += queryMatches * 2

            // Additional penalty for generic words that might cause false matches
            const genericWords = ['black', 'green', 'red', 'blue', 'olive', 'tan', 'brown', 'z-kabura', 'kurtka', 'buty', 'polar']
            const genericMatches = genericWords.filter(word => urlLower.includes(word)).length
            score -= genericMatches * 1

            return { productLink, score, reason: 'scored' }
          })

          // Filter out negative scores and require minimum score of 75
          const MIN_SCORE = 75
          const validLinks = scoredLinks
            .filter(item => item.score >= MIN_SCORE && item.productLink)
            .sort((a, b) => b.score - a.score) as Array<{ productLink: ProductLink; score: number; reason: string }>

          if (validLinks.length === 0) {
            console.log(`  ⚠️  No relevant products found after filtering (minimum score: ${MIN_SCORE}) - skipping`)
            // Log what was filtered out for debugging
            const allScored = scoredLinks.filter(item => item.productLink).sort((a, b) => b.score - a.score)
            if (allScored.length > 0) {
              console.log('  Top scored (but below threshold):')
              allScored.slice(0, 3).forEach((item, idx) => {
                const slug = item.productLink.url.split('/p/').pop()?.split('?')[0] || ''
                console.log(`    ${idx + 1}. Score: ${item.score.toFixed(1)} - ${slug}`)
              })
            }
            productLinks = []
          } else {
            // Log scoring details
            console.log(`  Scoring results (minimum score: ${MIN_SCORE}):`)
            validLinks.forEach((item, idx) => {
              const slug = item.productLink.url.split('/p/').pop()?.split('?')[0] || ''
              const priceInfo = item.productLink.price ? ` (${item.productLink.price} PLN)` : ''
              const variantInfo = item.productLink.variant ? ` [${item.productLink.variant}]` : ''
              console.log(`    ${idx + 1}. Score: ${item.score.toFixed(1)} - ${slug}${priceInfo}${variantInfo}`)
            })

            // Take only the best match (or top 3 if scores are very close)
            const topScore = validLinks[0].score
            const threshold = Math.max(MIN_SCORE, topScore * 0.85) // 85% of top score, but at least MIN_SCORE

            const bestMatches = validLinks.filter(item => item.score >= threshold).slice(0, 3)
            productLinks = bestMatches.map(item => item.productLink).filter((link): link is ProductLink => link !== undefined)

            console.log(`  ✅ Selected ${productLinks.length} best match(es) (score >= ${threshold.toFixed(1)})`)
          }
        }

        if (productLinks.length > 0) {
          console.log(`Found ${productLinks.length} product(s):`)
          productLinks.forEach((productLink, idx) => {
            const priceInfo = productLink.price ? ` (${productLink.price} PLN)` : ''
            const variantInfo = productLink.variant ? ` [${productLink.variant}]` : ''
            console.log(`  ${idx + 1}. ${productLink.url}${priceInfo}${variantInfo}`)
          })

          results.push({
            productId: product.id,
            productName: product.name,
            foundUrls: productLinks
          })
        } else {
          console.log('  No products found')
          results.push({
            productId: product.id,
            productName: product.name,
            foundUrls: []
          })
        }

        // Small delay between searches to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1500))
      } catch (error) {
        console.error(`Error searching for ${product.name}:`, error)
        results.push({
          productId: product.id,
          productName: product.name,
          foundUrls: []
        })
      }
    }

    // Update the JSON file
    console.log('\n\nUpdating catalogue_items.json...')
    updateJsonFile(jsonPath, results)

    const foundCount = results.filter(r => r.foundUrls.length > 0).length
    console.log(`\nCompleted! Found URLs for ${foundCount} out of ${products.length} products`)

    // Close readline interface if it was opened
    if (rl) {
      rl.close()
    }
  })
})


