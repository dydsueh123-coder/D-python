export interface AutomationScore {
  survey_id: number
  total_responses: number
  avg_time_hours: number
  avg_frequency_per_month: number
  automation_score: number
  priority_rank: number
}

export interface DashboardStats {
  total_surveys: number
  active_surveys: number
  total_responses: number
  total_recordings: number
}
