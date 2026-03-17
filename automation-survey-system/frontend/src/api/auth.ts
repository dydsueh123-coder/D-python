import apiClient from './client'
import type { LoginRequest, LoginResponse, User } from '../types/auth'

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', data),

  logout: () =>
    apiClient.post('/auth/logout'),

  getMe: () =>
    apiClient.get<User>('/auth/me'),
}
