import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Typography, Card, Spin, Alert, Button, Tag, Progress,
  Statistic, Row, Col, Table, Divider, Space
} from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { analyticsApi } from '../api/analytics'
import type { SurveyAnalytics, QuestionStats } from '../types/analytics'

const { Title, Text } = Typography

const statusColor: Record<string, string> = {
  draft: 'default', active: 'green', closed: 'red',
}
const statusLabel: Record<string, string> = {
  draft: '초안', active: '진행중', closed: '종료',
}

function QuestionStatCard({ qs, index }: { qs: QuestionStats; index: number }) {
  const { stats, question_type } = qs

  const renderStats = () => {
    if (question_type === 'scale' && stats.avg !== undefined) {
      const dist = stats.distribution ?? {}
      return (
        <div>
          <Row gutter={16} style={{ marginBottom: 12 }}>
            <Col span={8}>
              <Statistic title="평균" value={stats.avg} suffix="/ 5" precision={2} />
            </Col>
            <Col span={8}>
              <Statistic title="최솟값" value={stats.min} />
            </Col>
            <Col span={8}>
              <Statistic title="최댓값" value={stats.max} />
            </Col>
          </Row>
          <div>
            {[1, 2, 3, 4, 5].map((v) => {
              const cnt = dist[v] ?? 0
              const pct = qs.response_count > 0
                ? Math.round((cnt / qs.response_count) * 100)
                : 0
              return (
                <div key={v} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <Text style={{ width: 16 }}>{v}</Text>
                  <Progress percent={pct} size="small" style={{ flex: 1 }} showInfo={false} />
                  <Text type="secondary" style={{ width: 60 }}>{cnt}명 ({pct}%)</Text>
                </div>
              )
            })}
          </div>
        </div>
      )
    }

    if ((question_type === 'radio' || question_type === 'checkbox') && stats.choices) {
      const choices = stats.choices
      const total = Object.values(choices).reduce((a, b) => a + b, 0)
      return (
        <div>
          {Object.entries(choices)
            .sort(([, a], [, b]) => b - a)
            .map(([choice, cnt]) => {
              const pct = total > 0 ? Math.round((cnt / total) * 100) : 0
              return (
                <div key={choice} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <Text style={{ minWidth: 120, flexShrink: 0 }}>{choice}</Text>
                  <Progress percent={pct} size="small" style={{ flex: 1 }} showInfo={false} />
                  <Text type="secondary" style={{ width: 70 }}>{cnt}명 ({pct}%)</Text>
                </div>
              )
            })}
        </div>
      )
    }

    // text / textarea
    return <Text type="secondary">주관식 답변 {stats.answered ?? qs.response_count}건</Text>
  }

  return (
    <Card
      size="small"
      style={{ marginBottom: 16 }}
      title={
        <Space>
          <Text strong>{index + 1}. {qs.question_text}</Text>
          <Tag>{qs.question_type}</Tag>
          <Text type="secondary" style={{ fontSize: 12 }}>
            응답 {qs.response_count}건 ({qs.response_rate}%)
          </Text>
        </Space>
      }
    >
      {renderStats()}
    </Card>
  )
}

function SurveyAnalyticsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<SurveyAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    analyticsApi.getSurveyAnalytics(Number(id))
      .then((res) => setData(res.data))
      .catch(() => setError('통계 데이터를 불러오는 중 오류가 발생했습니다.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
  if (error) return <Alert type="error" message={error} showIcon />
  if (!data) return null

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => navigate('/admin')}
      >
        대시보드로
      </Button>

      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Title level={4} style={{ margin: 0 }}>{data.survey_title}</Title>
          <Tag color={statusColor[data.status]}>{statusLabel[data.status]}</Tag>
        </Space>
        <Row gutter={32} style={{ marginTop: 16 }}>
          <Col>
            <Statistic title="총 응답자" value={data.total_responses} suffix="명" />
          </Col>
          <Col>
            <Statistic
              title="척도 평균"
              value={data.avg_scale_score > 0 ? data.avg_scale_score : '-'}
              suffix={data.avg_scale_score > 0 ? '/ 5' : ''}
              precision={2}
            />
          </Col>
          <Col>
            <Statistic title="총 질문 수" value={data.questions.length} suffix="개" />
          </Col>
        </Row>
      </Card>

      <Divider orientation="left">질문별 응답 통계</Divider>

      {data.questions.map((qs, idx) => (
        <QuestionStatCard key={qs.question_id} qs={qs} index={idx} />
      ))}
    </div>
  )
}

export default SurveyAnalyticsPage
