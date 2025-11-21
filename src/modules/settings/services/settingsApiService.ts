// modules/settings/services/settingsApiService.ts
import { apiClient } from '@/shared/services/apiClient'
import type { ISettingsService, Settings, UpdateSettingsData } from '@/modules/settings/types/settings.type'

class SettingsApiService implements ISettingsService {
  async getSettings(): Promise<Settings> {
    const response = await apiClient.get<Settings>('/me/settings')
    return response.data
  }

  async updateSettings(data: UpdateSettingsData): Promise<Settings> {
    const response = await apiClient.patch<Settings>('/me/settings', data)
    return response.data
  }
}

export const settingsApiService = new SettingsApiService()


