import { config } from '@/shared/config/config'

let recaptchaLoaded = false
let recaptchaLoadPromise: Promise<void> | null = null

/**
 * Load reCAPTCHA v3 script
 */
export function loadRecaptchaScript(): Promise<void> {
  if (recaptchaLoaded) {
    return Promise.resolve()
  }

  if (recaptchaLoadPromise) {
    return recaptchaLoadPromise
  }

  if (!config.recaptcha.enabled) {
    return Promise.resolve()
  }

  recaptchaLoadPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://www.google.com/recaptcha/api.js?render=${config.recaptcha.siteKey}`
    script.async = true
    script.defer = true

    script.onload = () => {
      recaptchaLoaded = true
      resolve()
    }

    script.onerror = () => {
      reject(new Error('Failed to load reCAPTCHA script'))
    }

    document.head.appendChild(script)
  })

  return recaptchaLoadPromise
}

/**
 * Execute reCAPTCHA and get token
 */
export async function executeRecaptcha(action: string): Promise<string | null> {
  if (!config.recaptcha.enabled) {
    return null
  }

  try {
    await loadRecaptchaScript()

    if (!window.grecaptcha) {
      console.warn('reCAPTCHA not loaded')
      return null
    }

    return await window.grecaptcha.execute(config.recaptcha.siteKey, { action })
  }
  catch (error) {
    console.error('reCAPTCHA execution failed:', error)
    return null
  }
}

// Type declaration for window.grecaptcha
declare global {
  interface Window {
    grecaptcha: {
      execute: (siteKey: string, options: { action: string }) => Promise<string>
      ready: (callback: () => void) => void
    }
  }
}
