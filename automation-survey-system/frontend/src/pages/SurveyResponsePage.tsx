import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Form, Button, Typography, Spin, Alert, Result, Card, Divider, Space, Tag
} from 'antd'
import { CheckCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { surveysApi } from '../api/surveys'
import QuestionRenderer from '../components/survey/QuestionRenderer'
import type { SurveyDetail, SurveyResponse, AnswerInput } from '../types/survey'

const { Title, Paragraph, Text } = Typography

const statusLabel: Record<string, string> = {
  draft: '초안', active: '진행중', closed: '종료',
}
const statusColor: Record<string, string> = {
  draft: 'default', active: 'green', closed: 'red',
}

function SurveyResponsePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const [survey, setSurvey] = useState<SurveyDetail | null>(null)
  const [myResponse, setMyResponse] = useState<SurveyResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const surveyId = Number(id)

  useEffect(() => {
    if (!surveyId) return
    Promise.all([
      surveysApi.get(surveyId),
      surveysApi.getMyResponse(surveyId).catch(() => null),
    ])
      .then(([surveyRes, responseRes]) => {
        setSurvey(surveyRes.data)
        if (responseRes) setMyResponse(responseRes.data)
      })
      .catch(() => setError('설문을 불러오는 중 오류가 발생했습니다.'))
      .finally(() => setLoading(false))
  }, [surveyId])

  const handleSubmit = async (values: Record<string, unknown>) => {
    if (!survey) return
    setSubmitting(true)
    setError(null)

    // form values → AnswerInput[] 변환
    const answers: AnswerInput[] = survey.questions.map((q) => {
      const value = values[`q_${q.id}`]
      if (q.question_type === 'text' || q.question_type === 'textarea') {
        return { question_id: q.id, answer_text: value as string }
      }
      // radio/checkbox/scale → answer_data
      return { question_id: q.id, answer_data: value }
    }).filter((a) => a.answer_text !== undefined || a.answer_data !== undefined)

    try {
      const res = await surveysApi.submitResponse(surveyId, answers)
      setMyResponse(res.data)
      setSubmitted(true)
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { error?: string } } })
        ?.response?.data?.error ?? '제출 중 오류가 발생했습니다.'
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (error && !survey) {
    return <Alert type="error" message={error} showIcon />
  }

  if (!survey) {
    return <Alert type="warning" message="설문을 찾을 수 없습니다." showIcon />
  }

  // 이미 응답했거나 방금 제출 완료
  if (myResponse || submitted) {
    return (
      <Result
        icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
        title="응답이 완료되었습니다"
        subTitle={`"${survey.title}" 설문에 응답해 주셔서 감사합니다.`}
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/surveys')}>
            설문 목록으로
          </Button>
        }
      />
    )
  }

  // 설문이 active가 아닌 경우
  if (survey.status !== 'active') {
    return (
      <div>
        <Button
          icon={<ArrowLeftOutlined />}
          style={{ marginBottom: 16 }}
          onClick={() => navigate('/surveys')}
        >
          목록으로
        </Button>
        <Alert
          type="warning"
          message={`이 설문은 현재 응답할 수 없습니다. (상태: ${statusLabel[survey.status]})`}
          showIcon
        />
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => navigate('/surveys')}
      >
        목록으로
      </Button>

      <Card>
        {/* 설문 헤더 */}
        <Space align="center" style={{ marginBottom: 4 }}>
          <Title level={4} style={{ margin: 0 }}>{survey.title}</Title>
          <Tag color={statusColor[survey.status]}>{statusLabel[survey.status]}</Tag>
        </Space>

        {survey.description && (
          <Paragraph type="secondary" style={{ marginTop: 8 }}>
            {survey.description}
          </Paragraph>
        )}

        <Space style={{ marginBottom: 8 }}>
          {survey.start_date && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              시작: {new Date(survey.start_date).toLocaleDateString()}
            </Text>
          )}
          {survey.end_date && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              마감: {new Date(survey.end_date).toLocaleDateString()}
            </Text>
          )}
        </Space>

        <Divider />

        {error && (
          <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />
        )}

        {/* 질문 폼 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          requiredMark={false}
        >
          {survey.questions.map((q, idx) => (
            <QuestionRenderer key={q.id} question={q} index={idx} />
          ))}

          <Divider />

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={submitting}
              size="large"
              block
            >
              응답 제출
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default SurveyResponsePage
