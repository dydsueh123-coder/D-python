import apiClient from './client'
import type { User } from '../types/auth'

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  pages: number
}

export const adminApi = {
  listUsers: (params?: { page?: number; per_page?: number }) =>
    apiClient.get<UserListResponse>('/admin/users', { params }),

  setAdmin: (userId: number, isAdmin: boolean) =>
    apiClient.put<User>(`/admin/users/${userId}/admin`, { is_admin: isAdmin }),
}
