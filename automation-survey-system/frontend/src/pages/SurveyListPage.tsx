import { useEffect, useState } from 'react'
import { Typography, Table, Tag, Empty } from 'antd'
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

const columns: ColumnsType<Survey> = [
  { title: '제목', dataIndex: 'title', key: 'title' },
  {
    title: '상태',
    dataIndex: 'status',
    key: 'status',
    render: (s: string) => <Tag color={statusColor[s] ?? 'default'}>{statusLabel[s] ?? s}</Tag>,
  },
  { title: '시작일', dataIndex: 'start_date', key: 'start_date', render: (v: string | null) => v ?? '-' },
  { title: '종료일', dataIndex: 'end_date', key: 'end_date', render: (v: string | null) => v ?? '-' },
]

function SurveyListPage() {
  const [surveys, setSurveys] = useState<Survey[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    surveysApi
      .list()
      .then((res) => setSurveys(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <Title level={4}>설문 목록</Title>
      <Table
        columns={columns}
        dataSource={surveys}
        rowKey="id"
        loading={loading}
        locale={{ emptyText: <Empty description="설문이 없습니다" /> }}
      />
    </div>
  )
}

export default SurveyListPage
