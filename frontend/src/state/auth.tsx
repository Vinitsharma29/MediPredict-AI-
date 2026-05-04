import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api, setAuthToken } from '../api/client'

type Me = { id: number; email: string; role: 'doctor' | 'patient'; full_name?: string | null }

type AuthCtx = {
  token: string | null
  me: Me | null
  loadingMe: boolean
  login: (email: string, password: string) => Promise<Me>
  logout: () => void
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('mp_token'))
  const [me, setMe] = useState<Me | null>(null)
  const [loadingMe, setLoadingMe] = useState(false)

  async function fetchMe(t: string) {
    setLoadingMe(true)
    try {
      setAuthToken(t)
      const r = await api.get('/auth/me')
      setMe(r.data)
      return r.data as Me
    } catch {
      setMe(null)
      setToken(null)
      localStorage.removeItem('mp_token')
      setAuthToken(null)
      throw new Error('Session expired')
    } finally {
      setLoadingMe(false)
    }
  }

  useEffect(() => {
    if (!token) {
      setMe(null)
      setAuthToken(null)
      return
    }
    // On refresh, resolve /me once before enforcing role-based routing.
    fetchMe(token).catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  const value = useMemo<AuthCtx>(
    () => ({
      token,
      me,
      loadingMe,
      login: async (email, password) => {
        const r = await api.post('/auth/login', { email, password })
        const t = r.data.access_token as string
        localStorage.setItem('mp_token', t)
        setToken(t)
        return await fetchMe(t)
      },
      logout: () => {
        localStorage.removeItem('mp_token')
        setToken(null)
        setMe(null)
        setAuthToken(null)
      }
    }),
    [token, me, loadingMe]
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth() {
  const v = useContext(Ctx)
  if (!v) throw new Error('AuthProvider missing')
  return v
}
