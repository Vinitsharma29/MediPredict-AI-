import AutoGraphRoundedIcon from '@mui/icons-material/AutoGraphRounded'
import PsychologyRoundedIcon from '@mui/icons-material/PsychologyRounded'
import VerifiedRoundedIcon from '@mui/icons-material/VerifiedRounded'
import { Box, Button, Card, CardContent, Chip, Container, Grid, Stack, Typography } from '@mui/material'
import { useNavigate } from 'react-router-dom'

export default function LandingPage() {
  const nav = useNavigate()

  return (
    <Box>
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 9 } }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={7}>
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip icon={<AutoGraphRoundedIcon />} label="Live risk prediction" />
                <Chip icon={<PsychologyRoundedIcon />} label="Explainable AI (SHAP)" />
                <Chip icon={<VerifiedRoundedIcon />} label="Doctor workflow" />
              </Stack>

              <Typography variant="h3">MediPredict AI</Typography>

              <Typography sx={{ color: 'text.secondary', fontSize: 18, maxWidth: 560 }}>
                A browser-based clinical decision support system that helps doctors flag early disease risks and act faster.
              </Typography>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button variant="contained" size="large" onClick={() => nav('/login')}>
                  Request Demo
                </Button>
                <Button variant="outlined" size="large" onClick={() => nav('/login')}>
                  Open Dashboard
                </Button>
              </Stack>

              <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>
                Built for real clinics: fast intake, live risk scoring, explainable drivers, and actionable next steps.
              </Typography>
            </Stack>
          </Grid>

          <Grid item xs={12} md={5}>
            <Card>
              <CardContent>
                <Typography sx={{ fontWeight: 900, mb: 1 }}>Investor Mode</Typography>
                <Stack spacing={1.2}>
                  <Typography><b>Problem:</b> Late diagnosis causes preventable deaths</Typography>
                  <Typography><b>Solution:</b> AI-powered early risk prediction + explainable drivers</Typography>
                  <Typography><b>Market:</b> Hospitals, clinics, diagnostics</Typography>
                  <Typography><b>Revenue:</b> SaaS ₹5,000 – ₹20,000 per hospital/month</Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={2} sx={{ mt: 5 }}>
          {[
            { t: 'Clinical-grade UI', d: 'Clean, responsive dashboards suited for hospital workflows.' },
            { t: 'Explainable AI', d: 'SHAP-based risk drivers shown with charts for transparency.' },
            { t: 'Doctor workflow', d: 'Review, add notes, approve/reject suggestions, export PDF.' }
          ].map((x) => (
            <Grid item xs={12} md={4} key={x.t}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography sx={{ fontWeight: 900 }}>{x.t}</Typography>
                  <Typography sx={{ color: 'text.secondary', mt: 0.5 }}>{x.d}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  )
}
