import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography, Row, Col, Card, Statistic, Table, Tag, Spin, Alert,
  Progress, Tooltip, Button, Space
} from 'antd'
import {
  FileTextOutlined, CheckCircleOutlined, TeamOutlined,
  MessageOutlined, TrophyOutlined, BarChartOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { analyticsApi } from '../api/analytics'
import type { DashboardStats, PriorityItem } from '../types/analytics'

const { Title } = Typography

const statusColor: Record<string, string> = {
  draft: 'default', active: 'green', closed: 'red',
}
const statusLabel: Record<string, string> = {
  draft: '초안', active: '진행중', closed: '종료',
}

// 자동화 점수 → 색상 (높을수록 빨간색)
function scoreColor(score: number, maxScore: number): string {
  const ratio = maxScore > 0 ? score / maxScore : 0
  if (ratio >= 0.7) return '#f5222d'
  if (ratio >= 0.4) return '#fa8c16'
  return '#52c41a'
}

function AdminDashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [ranking, setRanking] = useState<PriorityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      analyticsApi.getDashboardStats(),
      analyticsApi.getPriorityRanking(),
    ])
      .then(([statsRes, rankingRes]) => {
        setStats(statsRes.data)
        setRanking(rankingRes.data)
      })
      .catch(() => setError('데이터를 불러오는 중 오류가 발생했습니다.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
  if (error) return <Alert type="error" message={error} showIcon />

  const maxScore = ranking.length > 0 ? ranking[0].automation_score : 1

  const columns: ColumnsType<PriorityItem> = [
    {
      title: '순위',
      dataIndex: 'priority_rank',
      key: 'rank',
      width: 60,
      render: (rank: number) => (
        rank <= 3
          ? <TrophyOutlined style={{ color: ['#FFD700', '#C0C0C0', '#CD7F32'][rank - 1], fontSize: 18 }} />
          : <span style={{ color: '#999' }}>{rank}</span>
      ),
    },
    {
      title: '설문 제목',
      dataIndex: 'survey_title',
      key: 'title',
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (s: string) => <Tag color={statusColor[s]}>{statusLabel[s]}</Tag>,
    },
    {
      title: '응답 수',
      dataIndex: 'total_responses',
      key: 'responses',
      width: 90,
      align: 'right',
    },
    {
      title: '평균 척도',
      dataIndex: 'avg_scale_score',
      key: 'avg_scale',
      width: 110,
      align: 'right',
      render: (v: number) => v > 0 ? `${v.toFixed(2)} / 5` : '-',
    },
    {
      title: '자동화 점수',
      dataIndex: 'automation_score',
      key: 'score',
      width: 180,
      render: (score: number) => (
        <Tooltip title={`점수: ${score.toFixed(2)}`}>
          <Progress
            percent={Math.round((score / maxScore) * 100)}
            strokeColor={scoreColor(score, maxScore)}
            size="small"
            format={(pct) => `${pct}%`}
          />
        </Tooltip>
      ),
    },
    {
      title: '',
      key: 'action',
      width: 80,
      render: (_: unknown, record: PriorityItem) => (
        <Button
          size="small"
          icon={<BarChartOutlined />}
          onClick={() => navigate(`/admin/surveys/${record.survey_id}/analytics`)}
        >
          상세
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 20 }}>
        <Title level={4} style={{ margin: 0 }}>관리자 대시보드</Title>
        <Button onClick={() => navigate('/admin/users')}>사용자 관리</Button>
      </Space>

      {/* 요약 카드 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic
              title="전체 설문"
              value={stats?.total_surveys}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="진행중"
              value={stats?.active_surveys}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="초안"
              value={stats?.draft_surveys}
              valueStyle={{ color: '#999' }}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="종료"
              value={stats?.closed_surveys}
              valueStyle={{ color: '#f5222d' }}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="총 응답 수"
              value={stats?.total_responses}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="총 사용자"
              value={stats?.total_users}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 우선순위 랭킹 */}
      <Card
        title={
          <Space>
            <TrophyOutlined />
            <span>자동화 우선순위 랭킹</span>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={ranking}
          rowKey="survey_id"
          pagination={false}
          locale={{ emptyText: '집계할 응답 데이터가 없습니다.' }}
        />
      </Card>
    </div>
  )
}

export default AdminDashboardPage
