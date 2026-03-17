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
  question_count?: number
  response_count?: number
}

// 설문 상세 (질문 목록 포함)
export interface SurveyDetail extends Survey {
  questions: Question[]
}

export interface Question {
  id: number
  survey_id: number
  order_num: number
  question_type: QuestionType
  question_text: string
  is_required: boolean
  options: string[] | null
  created_at: string
}

export interface Answer {
  id: number
  question_id: number
  answer_text: string | null
  answer_data: unknown | null
}

export interface SurveyResponse {
  id: number
  survey_id: number
  user_id: number
  is_complete: boolean
  submitted_at: string | null
  created_at: string
  answers?: Answer[]
}

// 응답 제출 요청 payload
export interface AnswerInput {
  question_id: number
  answer_text?: string
  answer_data?: unknown
}
