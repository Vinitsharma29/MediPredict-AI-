import { Card, CardContent, Grid, Stack, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import AppShell from '../components/AppShell'
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function AnalyticsPage() {
  const [dist, setDist] = useState<any>({})
  const [trends, setTrends] = useState<any[]>([])

  useEffect(() => {
    api.get('/analytics/distribution').then((r) => setDist(r.data))
    api.get('/analytics/trends').then((r) => setTrends(r.data))
  }, [])

  const distRows = Object.entries(dist).flatMap(([disease, risks]: any) =>
    Object.entries(risks as any).map(([risk, count]) => ({ disease, risk, count }))
  )

  return (
    <AppShell title="Analytics">
      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Card sx={{ border: '1px solid rgba(0,0,0,0.06)' }}>
            <CardContent>
              <Typography sx={{ fontWeight: 900, mb: 1 }}>Disease distribution</Typography>
              <Stack sx={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distRows}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="disease" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" name="Count" fill="#0b5cff" />
                  </BarChart>
                </ResponsiveContainer>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={7}>
          <Card sx={{ border: '1px solid rgba(0,0,0,0.06)' }}>
            <CardContent>
              <Typography sx={{ fontWeight: 900, mb: 1 }}>Risk trends (30 days)</Typography>
              <Stack sx={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Low" stroke="#2e7d32" strokeWidth={2} />
                    <Line type="monotone" dataKey="Medium" stroke="#ed6c02" strokeWidth={2} />
                    <Line type="monotone" dataKey="High" stroke="#d32f2f" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </AppShell>
  )
}
