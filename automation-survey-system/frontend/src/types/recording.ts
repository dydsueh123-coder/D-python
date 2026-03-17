export type RecordingStatus = 'uploaded' | 'processing' | 'ready' | 'error'

export interface Recording {
  id: number
  user_id: number
  survey_response_id: number | null
  filename: string
  original_filename: string | null
  file_size: number | null
  duration_seconds: number | null
  status: RecordingStatus
  created_at: string
}
