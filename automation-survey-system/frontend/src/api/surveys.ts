import apiClient from './client'
import type { Survey } from '../types/survey'

export const surveysApi = {
  list: () =>
    apiClient.get<Survey[]>('/surveys'),

  get: (id: number) =>
    apiClient.get<Survey>(`/surveys/${id}`),
}
