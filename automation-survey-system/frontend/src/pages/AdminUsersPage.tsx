import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography, Table, Tag, Button, Switch, Space, message, Alert
} from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { adminApi } from '../api/admin'
import { useAuthStore } from '../stores/authStore'
import type { User } from '../types/auth'

const { Title } = Typography

function AdminUsersPage() {
  const navigate = useNavigate()
  const { user: me } = useAuthStore()
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toggling, setToggling] = useState<number | null>(null)

  const fetchUsers = (p: number) => {
    setLoading(true)
    adminApi.listUsers({ page: p, per_page: 30 })
      .then((res) => {
        setUsers(res.data.items)
        setTotal(res.data.total)
      })
      .catch(() => setError('사용자 목록을 불러오는 중 오류가 발생했습니다.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchUsers(page)
  }, [page])

  const handleAdminToggle = async (userId: number, isAdmin: boolean) => {
    setToggling(userId)
    try {
      const res = await adminApi.setAdmin(userId, isAdmin)
      setUsers((prev) => prev.map((u) => (u.id === userId ? res.data : u)))
      message.success(isAdmin ? '관리자 권한이 부여되었습니다.' : '관리자 권한이 해제되었습니다.')
    } catch {
      message.error('권한 변경 중 오류가 발생했습니다.')
    } finally {
      setToggling(null)
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: '사용자명',
      dataIndex: 'username',
      key: 'username',
      render: (v: string, record: User) => (
        <span>
          {v}
          {record.id === me?.id && <Tag color="blue" style={{ marginLeft: 8 }}>나</Tag>}
        </span>
      ),
    },
    { title: '이름', dataIndex: 'display_name', key: 'display_name' },
    { title: '부서', dataIndex: 'department', key: 'department', render: (v: string | null) => v ?? '-' },
    { title: '직위', dataIndex: 'position', key: 'position', render: (v: string | null) => v ?? '-' },
    { title: '이메일', dataIndex: 'email', key: 'email', render: (v: string | null) => v ?? '-' },
    {
      title: '관리자',
      dataIndex: 'is_admin',
      key: 'is_admin',
      width: 100,
      render: (isAdmin: boolean, record: User) => (
        <Switch
          checked={isAdmin}
          loading={toggling === record.id}
          disabled={record.id === me?.id}
          onChange={(checked) => handleAdminToggle(record.id, checked)}
        />
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/admin')}>
          대시보드로
        </Button>
        <Title level={4} style={{ margin: 0 }}>사용자 관리</Title>
      </Space>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          total,
          pageSize: 30,
          onChange: setPage,
          showTotal: (t) => `총 ${t}명`,
        }}
      />
    </div>
  )
}

export default AdminUsersPage
