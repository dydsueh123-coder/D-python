import apiClient from './client'
import type { DashboardStats, PriorityItem, SurveyAnalytics } from '../types/analytics'

export const analyticsApi = {
  getDashboardStats: () =>
    apiClient.get<DashboardStats>('/analytics/dashboard'),

  getPriorityRanking: () =>
    apiClient.get<PriorityItem[]>('/analytics/priority'),

  getSurveyAnalytics: (surveyId: number) =>
    apiClient.get<SurveyAnalytics>(`/analytics/surveys/${surveyId}`),
}
