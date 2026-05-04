import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import { useAuth } from '../state/auth'

export default function LoginPage() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('doctor@medipredict.ai')
  const [password, setPassword] = useState('Doctor@123')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  return (
    <AppShell title="Login">
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <Box sx={{ width: '100%', maxWidth: 460, mt: { xs: 2, md: 5 } }}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Typography sx={{ fontWeight: 800 }}>Secure access</Typography>
                {err && <Alert severity="error">{err}</Alert>}
                <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true)
                    setErr(null)
                    try {
                      const me = await login(email, password)
                      nav(me.role === 'doctor' ? '/doctor' : '/patient')
                    } catch (e: any) {
                      setErr(e?.response?.data?.detail || e?.message || 'Login failed')
                    } finally {
                      setBusy(false)
                    }
                  }}
                >
                  Login
                </Button>
                <Stack direction="row" spacing={1}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setEmail('doctor@medipredict.ai')
                      setPassword('Doctor@123')
                    }}
                  >
                    Use doctor demo
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setEmail('patient@medipredict.ai')
                      setPassword('Patient@123')
                    }}
                  >
                    Use patient demo
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </AppShell>
  )
}
