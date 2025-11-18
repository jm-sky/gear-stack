// shared/utils/typeGuards.ts
// This file is kept for potential future use but axios dependencies have been removed
// as the app is now fully client-side with localStorage

export interface ValidationErrorResponse {
  errors: Record<string, string[]>
}

// Note: ValidationError type removed as it was dependent on AxiosError
// If needed in the future, create a custom error type for client-side validation
