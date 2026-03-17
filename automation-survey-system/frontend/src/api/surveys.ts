import apiClient from './client'
import type { Survey, SurveyDetail, SurveyResponse, AnswerInput } from '../types/survey'

export interface SurveyListResponse {
  items: Survey[]
  total: number
  page: number
  pages: number
}

export const surveysApi = {
  list: (params?: { status?: string; page?: number; per_page?: number }) =>
    apiClient.get<SurveyListResponse>('/surveys/', { params }),

  get: (id: number) =>
    apiClient.get<SurveyDetail>(`/surveys/${id}`),

  submitResponse: (surveyId: number, answers: AnswerInput[]) =>
    apiClient.post<SurveyResponse>(`/surveys/${surveyId}/responses`, { answers }),

  getMyResponse: (surveyId: number) =>
    apiClient.get<SurveyResponse>(`/surveys/${surveyId}/responses/mine`),
}
