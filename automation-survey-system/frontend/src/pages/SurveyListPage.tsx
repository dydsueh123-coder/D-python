import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Typography, Table, Tag, Empty, Button, Space } from 'antd'
import { FormOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { surveysApi } from '../api/surveys'
import type { Survey } from '../types/survey'

const { Title } = Typography

const statusColor: Record<string, string> = {
  draft: 'default',
  active: 'green',
  closed: 'red',
}

const statusLabel: Record<string, string> = {
  draft: '초안',
  active: '진행중',
  closed: '종료',
}

function SurveyListPage() {
  const navigate = useNavigate()
  const [surveys, setSurveys] = useState<Survey[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  const fetchSurveys = (p: number) => {
    setLoading(true)
    surveysApi
      .list({ page: p, per_page: 20 })
      .then((res) => {
        setSurveys(res.data.items)
        setTotal(res.data.total)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchSurveys(page)
  }, [page])

  const columns: ColumnsType<Survey> = [
    {
      title: '제목',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (s: string) => (
        <Tag color={statusColor[s] ?? 'default'}>{statusLabel[s] ?? s}</Tag>
      ),
    },
    {
      title: '질문 수',
      dataIndex: 'question_count',
      key: 'question_count',
      width: 90,
      render: (v: number) => v ?? '-',
    },
    {
      title: '응답 수',
      dataIndex: 'response_count',
      key: 'response_count',
      width: 90,
      render: (v: number) => v ?? '-',
    },
    {
      title: '마감일',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 120,
      render: (v: string | null) =>
        v ? new Date(v).toLocaleDateString() : '-',
    },
    {
      title: '',
      key: 'action',
      width: 120,
      render: (_: unknown, record: Survey) =>
        record.status === 'active' ? (
          <Button
            type="primary"
            size="small"
            icon={<FormOutlined />}
            onClick={() => navigate(`/surveys/${record.id}/respond`)}
          >
            응답하기
          </Button>
        ) : (
          <Button
            size="small"
            onClick={() => navigate(`/surveys/${record.id}/respond`)}
          >
            보기
          </Button>
        ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>설문 목록</Title>
      </Space>
      <Table
        columns={columns}
        dataSource={surveys}
        rowKey="id"
        loading={loading}
        locale={{ emptyText: <Empty description="설문이 없습니다" /> }}
        pagination={{
          current: page,
          total,
          pageSize: 20,
          onChange: setPage,
          showTotal: (t) => `총 ${t}건`,
        }}
      />
    </div>
  )
}

export default SurveyListPage
