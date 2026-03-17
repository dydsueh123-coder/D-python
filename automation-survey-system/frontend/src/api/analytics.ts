import apiClient from './client'
import type { DashboardStats, AutomationScore } from '../types/analytics'

export const analyticsApi = {
  getDashboardStats: () =>
    apiClient.get<DashboardStats>('/analytics/stats'),

  getAutomationScores: () =>
    apiClient.get<AutomationScore[]>('/analytics/scores'),
}
