import { create } from 'zustand'
import type { Survey } from '../types/survey'

interface SurveyState {
  surveys: Survey[]
  currentSurvey: Survey | null
  setSurveys: (surveys: Survey[]) => void
  setCurrentSurvey: (survey: Survey | null) => void
}

export const useSurveyStore = create<SurveyState>((set) => ({
  surveys: [],
  currentSurvey: null,
  setSurveys: (surveys) => set({ surveys }),
  setCurrentSurvey: (survey) => set({ currentSurvey: survey }),
}))
