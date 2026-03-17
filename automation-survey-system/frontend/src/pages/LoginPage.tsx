import { useState } from 'react'
import { Form, Input, Button, Card, Typography, Alert } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

const { Title, Text } = Typography

interface LoginForm {
  username: string
  password: string
}

function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const { setUser } = useAuthStore()

  const from = (location.state as { from?: Location })?.from?.pathname ?? '/surveys'

  const handleSubmit = async (values: LoginForm) => {
    setLoading(true)
    setError(null)
    try {
      const res = await authApi.login(values)
      setUser(res.data.user)
      navigate(from, { replace: true })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '로그인에 실패했습니다.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f5f5f5' }}>
      <Card style={{ width: 360 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3}>업무 자동화 설문 시스템</Title>
          <Text type="secondary">Y.P. Lee, Mock & Partners 임직원 전용</Text>
        </div>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form onFinish={handleSubmit} layout="vertical">
          <Form.Item name="username" rules={[{ required: true, message: '사용자명을 입력하세요' }]}>
            <Input prefix={<UserOutlined />} placeholder="사용자명 (AD 계정)" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '비밀번호를 입력하세요' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="비밀번호" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              로그인
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default LoginPage
