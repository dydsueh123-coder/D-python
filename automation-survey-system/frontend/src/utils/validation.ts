export function isValidUsername(username: string): boolean {
  return /^[a-zA-Z0-9._-]{3,50}$/.test(username)
}
