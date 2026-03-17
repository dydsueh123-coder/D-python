export type SurveyStatus = 'draft' | 'active' | 'closed'
export type QuestionType = 'text' | 'textarea' | 'radio' | 'checkbox' | 'scale' | 'file'

export interface Survey {
  id: number
  title: string
  description: string | null
  status: SurveyStatus
  created_by: number | null
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
}

export interface Question {
  id: number
  survey_id: number
  order_num: number
  question_type: QuestionType
  question_text: string
  is_required: boolean
  options: string[] | null
}

export interface SurveyResponse {
  id: number
  survey_id: number
  user_id: number
  is_complete: boolean
  submitted_at: string | null
  created_at: string
}
