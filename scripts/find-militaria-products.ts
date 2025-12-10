import { test } from '@playwright/test'
import { readFileSync, writeFileSync } from 'fs'
import { join } from 'path'
import type { CatalogueItem, CatalogueItemShop } from '../backend/app/seeders/catalogue_items.types'

interface Product extends Partial<CatalogueItem> {
  id: string
  name: string
  brand: string
  model: string
  shops?: CatalogueItemShop[]
}

interface SearchResult {
  productId: string
  productName: string
  foundUrls: string[]
}

/**
 * Load products from JSON file
 */
function loadProductsFromJson(jsonPath: string): Product[] {
  const content = readFileSync(jsonPath, 'utf-8')
  return JSON.parse(content) as Product[]
}

/**
 * Generate search query for a product
 */
function generateSearchQuery(product: Product): string {
  // Try brand + model first
  if (product.brand && product.brand !== 'Generic' && product.brand !== 'Generic / MIL-SPEC') {
    return `${product.brand} ${product.model}`.trim()
  }
  // Fallback to product name
  return product.name
}

/**
 * Update catalogue_items.json with found URLs
 */
function updateJsonFile(jsonPath: string, results: SearchResult[]): void {
  try {
    const products = JSON.parse(readFileSync(jsonPath, 'utf-8')) as Product[]

    let updatedCount = 0
    for (const result of results) {
      if (result.foundUrls.length === 0) continue

      const product = products.find(p => p.id === result.productId)
      if (product) {
        product.shops = result.foundUrls.map(url => ({ url }))
        updatedCount++
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

    const allProducts = loadProductsFromJson(jsonPath)
    const products = allProducts.filter(p => !p.shops || p.shops.length === 0)

    console.log(`Found ${products.length} products needing shop URLs`)

    const results: SearchResult[] = []

    for (const product of products) {
      const searchQuery = generateSearchQuery(product)
      const encodedQuery = encodeURIComponent(searchQuery)
      const searchUrl = `https://militaria.pl/szukaj?q=${encodedQuery}`

      console.log(`\nSearching for: ${product.name}`)
      console.log(`Query: ${searchQuery}`)
      console.log(`URL: ${searchUrl}`)

      try {
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 })
        await page.waitForTimeout(2000) // Wait for page to load

        // Handle cookie consent (Cookiebot)
        try {
          // Wait a bit for cookie dialog to appear
          await page.waitForTimeout(1000)

          // Try to find and click "Accept all" or similar button in Cookiebot
          const cookieSelectors = [
            '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', // Cookiebot allow all (main selector)
            '#CybotCookiebotDialogBodyButtonAccept', // Alternative Cookiebot accept
            'button[id*="CybotCookiebotDialog"][id*="Allow"]', // Any Cookiebot allow button
            'button[id*="CybotCookiebotDialog"][id*="Accept"]', // Any Cookiebot accept button
            '[id*="cookiebot"] button[id*="allow"]', // Cookiebot allow (case insensitive)
            '[id*="cookiebot"] button[id*="accept"]', // Cookiebot accept (case insensitive)
            'button:has-text("Accept all")',
            'button:has-text("Akceptuj wszystkie")',
            'button:has-text("Allow all")',
          ]

          for (const selector of cookieSelectors) {
            try {
              const cookieButton = await page.$(selector)
              if (cookieButton && await cookieButton.isVisible()) {
                await cookieButton.click()
                console.log(`  Clicked cookie consent (${selector})`)
                await page.waitForTimeout(1500) // Wait for dialog to close
                break
              }
            } catch {
              // Try next selector
            }
          }
        } catch {
          // Cookie consent not found or already accepted, continue
        }

        await page.waitForTimeout(2000) // Wait after cookie consent

        // Wait for search results container to appear
        let productLinks: string[] = []
        try {
          // Wait for main content or product elements (best selectors from testing)
          await page.waitForSelector('main, [data-product-id], .product', { timeout: 5000 })

          // Look for product links specifically in search results
          // Use the best selectors we found: [data-product-id] and .product in main container
          productLinks = await page.evaluate(() => {
            const urls = new Set<string>()

            // Try to find products in main content area (search results)
            const main = document.querySelector('main')
            const searchContainer = main || document.body

            // Use data-product-id selector first (most specific - found 24 elements in tests)
            const productLinksWithId = searchContainer.querySelectorAll<HTMLAnchorElement>('[data-product-id] a[href*="/p/"]')

            if (productLinksWithId.length > 0) {
              productLinksWithId.forEach(link => {
                const href = link.href
                if (href.includes('/p/') && !href.includes('/szukaj') && !href.includes('/kategoria')) {
                  urls.add(href)
                }
              })
            }

            // Fallback to .product selector if no results
            if (urls.size === 0) {
              const productElements = searchContainer.querySelectorAll<HTMLAnchorElement>('.product a[href*="/p/"]')
              productElements.forEach(link => {
                const href = link.href
                if (href.includes('/p/') && !href.includes('/szukaj') && !href.includes('/kategoria')) {
                  urls.add(href)
                }
              })
            }

            return Array.from(urls).slice(0, 5) // Get first 5 unique results
          })
        } catch {
          // No products found, continue with empty array
        }

        if (productLinks.length > 0) {
          console.log(`Found ${productLinks.length} product(s):`)
          productLinks.forEach((url, idx) => {
            console.log(`  ${idx + 1}. ${url}`)
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
        try {
          await page.waitForTimeout(2000)
        } catch {
          // Timeout exceeded, but continue with next product
        }
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
  })
})


