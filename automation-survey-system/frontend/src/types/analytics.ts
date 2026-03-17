export interface DashboardStats {
  total_surveys: number
  active_surveys: number
  draft_surveys: number
  closed_surveys: number
  total_responses: number
  total_users: number
}

export interface PriorityItem {
  survey_id: number
  survey_title: string
  status: string
  total_responses: number
  avg_scale_score: number
  automation_score: number
  priority_rank: number
}

export interface QuestionStats {
  question_id: number
  question_text: string
  question_type: string
  response_count: number
  response_rate: number
  stats: {
    avg?: number
    min?: number
    max?: number
    distribution?: Record<number, number>
    choices?: Record<string, number>
    answered?: number
  }
}

export interface SurveyAnalytics {
  survey_id: number
  survey_title: string
  status: string
  total_responses: number
  avg_scale_score: number
  questions: QuestionStats[]
}
