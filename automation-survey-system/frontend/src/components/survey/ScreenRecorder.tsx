import { useRef } from 'react'
import { Button, Space, Typography, Alert, Progress, Tag, Tooltip } from 'antd'
import {
  VideoCameraOutlined, StopOutlined, UploadOutlined,
  RedoOutlined, CheckCircleOutlined, LoadingOutlined,
} from '@ant-design/icons'
import { useScreenRecorder } from '../../hooks/useScreenRecorder'

const { Text } = Typography

interface Props {
  surveyResponseId?: number
  onUploaded?: (recordingId: number) => void
}

// 초 → mm:ss
function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function ScreenRecorder({ surveyResponseId, onUploaded }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const {
    state, elapsedSeconds, blob, recording, errorMessage,
    startRecording, stopRecording, uploadRecording, reset,
  } = useScreenRecorder()

  // 녹화 완료 후 미리보기 URL 생성
  const previewUrl = blob ? URL.createObjectURL(blob) : null

  const handleUpload = async () => {
    await uploadRecording(surveyResponseId)
    if (recording) onUploaded?.(recording.id)
  }

  const stateTag = () => {
    switch (state) {
      case 'recording':
        return <Tag color="red" icon={<LoadingOutlined />}>녹화중 {formatTime(elapsedSeconds)}</Tag>
      case 'stopped':
        return <Tag color="orange">녹화 완료 ({formatTime(elapsedSeconds)})</Tag>
      case 'uploading':
        return <Tag color="blue" icon={<LoadingOutlined />}>업로드 중...</Tag>
      case 'done':
        return <Tag color="green" icon={<CheckCircleOutlined />}>업로드 완료</Tag>
      default:
        return null
    }
  }

  return (
    <div style={{ padding: '16px', background: '#fafafa', borderRadius: 8, border: '1px solid #f0f0f0' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <VideoCameraOutlined style={{ fontSize: 18, color: '#1890ff' }} />
          <Text strong>업무 화면 녹화 (선택사항)</Text>
          {stateTag()}
        </Space>

        <Text type="secondary" style={{ fontSize: 12 }}>
          현재 업무 화면을 녹화하면 자동화 검토에 도움이 됩니다. Chrome 화면 선택창이 열립니다.
        </Text>

        {errorMessage && (
          <Alert type="error" message={errorMessage} showIcon closable onClose={reset} />
        )}

        {/* 컨트롤 버튼 */}
        <Space>
          {state === 'idle' || state === 'error' ? (
            <Button
              icon={<VideoCameraOutlined />}
              onClick={startRecording}
              type="default"
            >
              녹화 시작
            </Button>
          ) : null}

          {state === 'requesting' && (
            <Button icon={<LoadingOutlined />} disabled>
              화면 선택 중...
            </Button>
          )}

          {state === 'recording' && (
            <Button
              icon={<StopOutlined />}
              danger
              onClick={stopRecording}
            >
              녹화 중지
            </Button>
          )}

          {state === 'stopped' && (
            <>
              <Button
                icon={<UploadOutlined />}
                type="primary"
                onClick={handleUpload}
              >
                업로드
              </Button>
              <Tooltip title="다시 녹화합니다">
                <Button icon={<RedoOutlined />} onClick={reset}>다시 녹화</Button>
              </Tooltip>
            </>
          )}

          {state === 'uploading' && (
            <Button icon={<LoadingOutlined />} disabled>
              업로드 중...
            </Button>
          )}

          {state === 'done' && (
            <Button icon={<RedoOutlined />} onClick={reset}>재녹화</Button>
          )}
        </Space>

        {/* 녹화 후 미리보기 */}
        {(state === 'stopped' || state === 'done') && previewUrl && (
          <video
            ref={videoRef}
            src={previewUrl}
            controls
            style={{ width: '100%', maxHeight: 240, borderRadius: 4, background: '#000' }}
          />
        )}

        {/* 업로드 완료 후 서버 재생 링크 */}
        {state === 'done' && recording && (
          <Alert
            type="success"
            message={
              <Space>
                <Text>녹화가 저장되었습니다.</Text>
                <a
                  href={`/api/recordings/${recording.id}/file`}
                  target="_blank"
                  rel="noreferrer"
                >
                  다시 보기
                </a>
              </Space>
            }
          />
        )}
      </Space>
    </div>
  )
}

export default ScreenRecorder
