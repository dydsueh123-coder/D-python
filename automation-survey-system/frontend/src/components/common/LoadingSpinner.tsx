import { Spin } from 'antd'

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large'
  fullScreen?: boolean
}

function LoadingSpinner({ size = 'default', fullScreen = false }: LoadingSpinnerProps) {
  if (fullScreen) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size={size} />
      </div>
    )
  }
  return <Spin size={size} />
}

export default LoadingSpinner
