import HealthAndSafetyRoundedIcon from '@mui/icons-material/HealthAndSafetyRounded'
import { AppBar, Avatar, Box, Button, Chip, Container, Stack, Toolbar, Typography } from '@mui/material'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/auth'

export default function AppShell({ title, children }: { title: string; children: React.ReactNode }) {
  const { me, logout } = useAuth()
  const nav = useNavigate()

  return (
    <Box>
      <AppBar position="sticky" elevation={0} color="transparent">
        <Toolbar sx={{ backdropFilter: 'blur(14px)' }}>
          <Container maxWidth="lg" sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Stack component={Link} to="/" direction="row" spacing={1.2} alignItems="center">
              <Avatar sx={{ bgcolor: 'primary.main', width: 34, height: 34 }}>
                <HealthAndSafetyRoundedIcon fontSize="small" />
              </Avatar>
              <Box>
                <Typography sx={{ fontWeight: 900, lineHeight: 1.1 }}>MediPredict AI</Typography>
                <Typography sx={{ fontSize: 12, color: 'text.secondary', lineHeight: 1.1 }}>Clinical decision support</Typography>
              </Box>
            </Stack>

            <Box sx={{ flex: 1 }} />

            <Stack direction="row" spacing={1} alignItems="center">
              {me?.role === 'doctor' && (
                <>
                  <Button size="small" component={Link} to="/doctor">Doctor</Button>
                  <Button size="small" component={Link} to="/analytics">Analytics</Button>
                </>
              )}
              {me?.role === 'patient' && <Button size="small" component={Link} to="/patient">Patient</Button>}

              {me && <Chip size="small" label={me.role.toUpperCase()} variant="outlined" />}

              {me ? (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    logout()
                    nav('/login')
                  }}
                >
                  Logout
                </Button>
              ) : (
                <Button size="small" variant="contained" onClick={() => nav('/login')}>Login</Button>
              )}
            </Stack>
          </Container>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Typography variant="h5" sx={{ textAlign: 'center', mb: 2 }}>
          {title}
        </Typography>
        {children}
      </Container>
    </Box>
  )
}
