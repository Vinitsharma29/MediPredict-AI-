import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#0b5cff' },
    secondary: { main: '#0bb3a9' },
    background: { default: '#f6f8fb', paper: '#ffffff' }
  },
  shape: { borderRadius: 16 },
  typography: {
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
    h3: { fontWeight: 900, letterSpacing: -0.8 },
    h5: { fontWeight: 900, letterSpacing: -0.2 }
  },
  components: {
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: '1px solid rgba(16, 24, 40, 0.08)',
          boxShadow: '0 10px 30px rgba(16, 24, 40, 0.06)'
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 12, fontWeight: 700 },
        contained: { boxShadow: '0 10px 20px rgba(11, 92, 255, 0.22)' }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'rgba(255,255,255,0.7)',
          borderBottom: '1px solid rgba(16, 24, 40, 0.08)'
        }
      }
    }
  }
})
