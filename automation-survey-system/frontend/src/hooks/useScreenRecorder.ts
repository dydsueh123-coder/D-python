import { useState, useRef, useCallback, useEffect } from 'react'
import { recordingsApi } from '../api/recordings'
import type { Recording } from '../types/recording'

export type RecorderState =
  | 'idle'
  | 'requesting'   // 화면 선택 대화상자 표시 중
  | 'recording'
  | 'stopped'      // 녹화 완료, 업로드 대기
  | 'uploading'
  | 'done'
  | 'error'

export interface UseScreenRecorderReturn {
  state: RecorderState
  elapsedSeconds: number
  blob: Blob | null
  recording: Recording | null
  errorMessage: string | null
  startRecording: () => Promise<void>
  stopRecording: () => void
  uploadRecording: (surveyResponseId?: number) => Promise<void>
  reset: () => void
}

export function useScreenRecorder(): UseScreenRecorderReturn {
  const [state, setState] = useState<RecorderState>('idle')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [blob, setBlob] = useState<Blob | null>(null)
  const [recording, setRecording] = useState<Recording | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  // 컴포넌트 언마운트 시 스트림 정리
  useEffect(() => {
    return () => {
      stopStream()
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
  }

  const startRecording = useCallback(async () => {
    setErrorMessage(null)
    setState('requesting')

    try {
      // Chrome: 화면 선택 다이얼로그 표시
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: 15 },  // 낮은 프레임율로 용량 절약
        audio: false,
      })
      streamRef.current = stream

      // 사용자가 공유 중지 버튼을 누르면 자동 정지
      stream.getVideoTracks()[0].addEventListener('ended', () => {
        stopRecording()
      })

      chunksRef.current = []
      const mr = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' })

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mr.onstop = () => {
        const recorded = new Blob(chunksRef.current, { type: 'video/webm' })
        setBlob(recorded)
        setState('stopped')
        stopStream()
        if (timerRef.current) clearInterval(timerRef.current)
      }

      mr.start(1000)  // 1초 단위 청크
      mediaRecorderRef.current = mr

      // 타이머
      startTimeRef.current = Date.now()
      timerRef.current = setInterval(() => {
        setElapsedSeconds(Math.floor((Date.now() - startTimeRef.current) / 1000))
      }, 1000)

      setState('recording')
    } catch (e: unknown) {
      stopStream()
      const err = e as { name?: string; message?: string }
      if (err.name === 'NotAllowedError') {
        setErrorMessage('화면 공유 권한이 거부되었습니다.')
      } else {
        setErrorMessage('화면 녹화를 시작할 수 없습니다.')
      }
      setState('error')
    }
  }, [])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const uploadRecording = useCallback(async (surveyResponseId?: number) => {
    if (!blob) return
    setState('uploading')

    try {
      const durationSeconds = Math.floor((Date.now() - startTimeRef.current) / 1000) || elapsedSeconds
      const res = await recordingsApi.upload(blob, surveyResponseId, durationSeconds)
      setRecording(res.data)
      setState('done')
    } catch {
      setErrorMessage('업로드 중 오류가 발생했습니다.')
      setState('error')
    }
  }, [blob, elapsedSeconds])

  const reset = useCallback(() => {
    stopStream()
    if (timerRef.current) clearInterval(timerRef.current)
    mediaRecorderRef.current = null
    chunksRef.current = []
    setBlob(null)
    setRecording(null)
    setElapsedSeconds(0)
    setErrorMessage(null)
    setState('idle')
  }, [])

  return {
    state,
    elapsedSeconds,
    blob,
    recording,
    errorMessage,
    startRecording,
    stopRecording,
    uploadRecording,
    reset,
  }
}
