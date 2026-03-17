import apiClient from './client'
import type { Recording } from '../types/recording'

export const recordingsApi = {
  list: () =>
    apiClient.get<Recording[]>('/recordings/'),

  upload: (
    blob: Blob,
    surveyResponseId?: number,
    durationSeconds?: number,
    onProgress?: (pct: number) => void,
  ) => {
    const formData = new FormData()
    formData.append('file', blob, 'recording.webm')
    if (surveyResponseId) formData.append('survey_response_id', String(surveyResponseId))
    if (durationSeconds) formData.append('duration_seconds', String(durationSeconds))

    return apiClient.post<Recording>('/recordings/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      },
    })
  },

  getFileUrl: (recordingId: number) =>
    `/api/recordings/${recordingId}/file`,

  delete: (recordingId: number) =>
    apiClient.delete(`/recordings/${recordingId}`),
}
