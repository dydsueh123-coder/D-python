import apiClient from './client'
import type { Survey, SurveyDetail, SurveyResponse, AnswerInput, Question } from '../types/survey'

export interface SurveyListResponse {
  items: Survey[]
  total: number
  page: number
  pages: number
}

export interface SurveyCreateInput {
  title: string
  description?: string
  start_date?: string
  end_date?: string
}

export interface QuestionInput {
  question_type: string
  question_text: string
  is_required?: boolean
  options?: string[]
}

export const surveysApi = {
  // ── 일반 ──────────────────────────────────────────────
  list: (params?: { status?: string; page?: number; per_page?: number }) =>
    apiClient.get<SurveyListResponse>('/surveys/', { params }),

  get: (id: number) =>
    apiClient.get<SurveyDetail>(`/surveys/${id}`),

  submitResponse: (surveyId: number, answers: AnswerInput[]) =>
    apiClient.post<SurveyResponse>(`/surveys/${surveyId}/responses`, { answers }),

  getMyResponse: (surveyId: number) =>
    apiClient.get<SurveyResponse>(`/surveys/${surveyId}/responses/mine`),

  // ── 관리자 — 설문 CRUD ────────────────────────────────
  create: (data: SurveyCreateInput) =>
    apiClient.post<Survey>('/surveys/', data),

  update: (id: number, data: Partial<SurveyCreateInput>) =>
    apiClient.put<Survey>(`/surveys/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/surveys/${id}`),

  activate: (id: number) =>
    apiClient.post<Survey>(`/surveys/${id}/activate`),

  close: (id: number) =>
    apiClient.post<Survey>(`/surveys/${id}/close`),

  // ── 관리자 — 질문 관리 ────────────────────────────────
  addQuestion: (surveyId: number, data: QuestionInput) =>
    apiClient.post<Question>(`/surveys/${surveyId}/questions`, data),

  updateQuestion: (surveyId: number, questionId: number, data: Partial<QuestionInput>) =>
    apiClient.put<Question>(`/surveys/${surveyId}/questions/${questionId}`, data),

  deleteQuestion: (surveyId: number, questionId: number) =>
    apiClient.delete(`/surveys/${surveyId}/questions/${questionId}`),

  reorderQuestions: (surveyId: number, order: { id: number; order_num: number }[]) =>
    apiClient.put<Question[]>(`/surveys/${surveyId}/questions/reorder`, order),
}
