import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,  // 세션 쿠키 포함
  headers: {
    'Content-Type': 'application/json',
  },
})

// 401 응답 시 로그인 페이지로 리디렉트
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
