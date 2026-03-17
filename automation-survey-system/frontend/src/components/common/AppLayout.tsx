import { Layout, Menu, Typography, Button } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { FormOutlined, LogoutOutlined, DashboardOutlined } from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'
import { authApi } from '../../api/auth'

const { Header, Sider, Content } = Layout
const { Text } = Typography

function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await authApi.logout()
    logout()
    navigate('/login')
  }

  // 현재 경로에 맞는 메뉴 키 선택
  const selectedKey = location.pathname.startsWith('/admin')
    ? '/admin'
    : '/surveys'

  const menuItems = [
    {
      key: '/surveys',
      icon: <FormOutlined />,
      label: '설문 목록',
    },
    // 관리자만 표시
    ...(user?.is_admin
      ? [
          {
            key: '/admin',
            icon: <DashboardOutlined />,
            label: '관리자 대시보드',
          },
        ]
      : []),
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="light">
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <Text strong>업무 자동화 설문</Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff', padding: '0 24px',
            display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Text style={{ marginRight: 16 }}>{user?.display_name ?? user?.username}</Text>
          <Button icon={<LogoutOutlined />} onClick={handleLogout}>로그아웃</Button>
        </Header>
        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout
