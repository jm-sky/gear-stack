import { isAxiosError } from 'axios'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { isValidationError } from '../utils/typeGuards'

export const useHandleError = () => {
  const { t } = useI18n()

  const handleError = (error: unknown, setErrors?: (errors: Record<string, string[]>) => void) => {
    if (isValidationError(error) && setErrors) {
      setErrors(error.response.data.errors)
    } else if (isAxiosError(error)) {
      toast.error(error.response?.data.message ?? error.response?.data.detail ?? t('errors.generic'))
    } else {
      toast.error(t('errors.generic'))
    }
  }

  return {
    handleError,
  }
}
