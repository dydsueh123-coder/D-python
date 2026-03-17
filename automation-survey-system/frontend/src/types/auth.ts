export interface User {
  id: number
  username: string
  display_name: string
  email: string | null
  department: string | null
  position: string | null
  is_admin: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  user: User
  message: string
}
