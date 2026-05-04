import WarningAmberRoundedIcon from '@mui/icons-material/WarningAmberRounded'
import {Alert, Box, Button, Card, CardContent, Divider, Grid, List, ListItemButton, ListItemText, Snackbar, Stack, TextField, Typography, Chip } from '@mui/material'
import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import { RiskChip } from '../components/RiskChip'
import { api } from '../api/client'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

type PatientRow = {
  id: number
  name: string
  age: number
  gender: string
  has_active_alert?: boolean
  active_alert_id?: number | null
  latest_prediction: null | { id: number; disease: string; risk_level: string; probability: number; doctor_decision?: string | null }
}

type PatientDetail = {
  patient: any
  active_alert?: any
  predictions: any[]
  reports: any[]
}

type ActiveAlert = {
  alert_id: number
  patient_id: number
  patient_name: string
  risk_level: string
  probability: number
  timestamp: string
  status: string
}

function toChart(top: { feature: string; shap: number; value: number }[]) {
  return top.map((t) => ({ name: t.feature, impact: Math.abs(t.shap) }))
}

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function DoctorDashboard() {
  const [rows, setRows] = useState<PatientRow[]>([])
  const [alerts, setAlerts] = useState<ActiveAlert[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [detail, setDetail] = useState<PatientDetail | null>(null)
  const [note, setNote] = useState('')
  const [chatMsg, setChatMsg] = useState('Explain why the risk is high and what tests to order.')
  const [chatOut, setChatOut] = useState<string>('')
  const [demoStep, setDemoStep] = useState<string | null>(null)

  const [toast, setToast] = useState<{ open: boolean; msg: string; sev: 'success' | 'error' | 'info' }>(
    { open: false, msg: '', sev: 'info' }
  )

  async function refresh() {
    const r = await api.get('/doctor/patients')
    setRows(r.data)
  }

  async function refreshAlerts() {
    const r = await api.get('/alerts/active')
    setAlerts(r.data)
  }

  async function loadDetail(pid: number) {
    setSelectedId(pid)
    const r = await api.get(`/doctor/patient/${pid}`)
    setDetail(r.data)
    setNote('')
    setChatOut('')
  }

  useEffect(() => {
    refresh()
    refreshAlerts()
  }, [])

  return (
    <AppShell title="Doctor Dashboard">
      <Snackbar
        open={toast.open}
        autoHideDuration={2500}
        onClose={() => setToast((t) => ({ ...t, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={toast.sev} variant="filled" onClose={() => setToast((t) => ({ ...t, open: false }))}>
          {toast.msg}
        </Alert>
      </Snackbar>

      {alerts.length > 0 && (
        <Box
          sx={{
            mb: 2,
            p: 1.5,
            borderRadius: 2,
            background: 'rgba(211, 47, 47, 0.10)',
            border: '1px solid rgba(211, 47, 47, 0.35)',
            display: 'flex',
            alignItems: 'center',
            gap: 1.2,
            animation: 'mpPulse 1.2s ease-in-out infinite'
          }}
        >
          <WarningAmberRoundedIcon sx={{ color: 'error.main', animation: 'mpBlink 1s ease-in-out infinite' }} />
          <Typography sx={{ fontWeight: 900, color: 'error.main' }}>
            Critical Patient Alert – Immediate Medical Attention Required
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Button size="small" variant="contained" color="error" onClick={refreshAlerts}>
            Refresh Alerts
          </Button>
        </Box>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" spacing={1} justifyContent="space-between" alignItems="center">
                <Typography sx={{ fontWeight: 900 }}>Patients</Typography>
                <Stack direction="row" spacing={1}>
                  <Button size="small" variant="outlined" onClick={async () => { await refresh(); await refreshAlerts() }}>
                    Refresh
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={async () => {
                      try {
                        setDemoStep('1) Auto-fill patient data')
                        const sim = await api.get('/patients/simulate/case')
                        setDemoStep('2) Save patient')
                        const created = await api.post('/patients', sim.data)
                        const pid = created.data.id as number
                        setDemoStep('3) Run AI prediction')
                        await api.post('/predictions/run', { patient_id: pid, disease: 'heart' })
                        await api.post('/predictions/run', { patient_id: pid, disease: 'diabetes' })
                        setDemoStep('4) Switch to doctor view')
                        await refresh()
                        await refreshAlerts()
                        await loadDetail(pid)
                        setDemoStep('5) Doctor reviews + adds notes')
                        setTimeout(() => setDemoStep(null), 2500)
                      } catch (e: any) {
                        setToast({ open: true, msg: e?.response?.data?.detail || 'Demo failed', sev: 'error' })
                        setDemoStep(null)
                      }
                    }}
                  >
                    Start Demo
                  </Button>
                </Stack>
              </Stack>

              {demoStep && (
                <Box sx={{ mt: 1 }}>
                  <Box
                    component="span"
                    sx={{
                      display: 'inline-block',
                      px: 1.25,
                      py: 0.75,
                      borderRadius: 999,
                      background: 'rgba(11, 92, 255, 0.10)',
                      color: 'primary.main',
                      fontWeight: 800,
                      fontSize: 12
                    }}
                  >
                    {demoStep}
                  </Box>
                </Box>
              )}

              {alerts.length > 0 && (
                <>
                  <Divider sx={{ my: 1.5 }} />
                  <Typography sx={{ fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WarningAmberRoundedIcon color="error" fontSize="small" /> Critical Alerts
                  </Typography>
                  <Stack spacing={1} sx={{ mt: 1 }}>
                    {alerts.slice(0, 6).map((a) => (
                      <Box
                        key={a.alert_id}
                        sx={{
                          p: 1,
                          borderRadius: 2,
                          border: '1px solid rgba(211, 47, 47, 0.25)',
                          background: 'rgba(211, 47, 47, 0.06)'
                        }}
                      >
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography sx={{ fontWeight: 900, fontSize: 13 }}>{a.patient_name}</Typography>
                          <RiskChip risk={a.risk_level} prob={a.probability} />
                        </Stack>
                        <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                          <Button size="small" variant="contained" color="error" onClick={() => loadDetail(a.patient_id)}>
                            View
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={async () => {
                              try {
                                await api.post(`/alerts/${a.alert_id}/resolve`)
                                await refreshAlerts()
                                await refresh()
                                setToast({ open: true, msg: 'Marked as handled', sev: 'success' })
                              } catch (e: any) {
                                setToast({ open: true, msg: e?.response?.data?.detail || 'Update failed', sev: 'error' })
                              }
                            }}
                          >
                            Handled
                          </Button>
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                </>
              )}

              <Divider sx={{ my: 1.5 }} />

              <List dense sx={{ maxHeight: 380, overflow: 'auto' }}>
                {rows.map((p) => (
                  <ListItemButton key={p.id} selected={p.id === selectedId} onClick={() => loadDetail(p.id)}>
                    <ListItemText
                      primary={
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <span>{p.name}</span>
                          {p.has_active_alert ? (
                            <Chip size="small" color="error" label="🚨 Critical" />
                          ) : (
                            p.latest_prediction && <RiskChip risk={p.latest_prediction.risk_level} prob={p.latest_prediction.probability} />
                          )}
                        </Stack>
                      }
                      secondary={`${p.age} • ${p.gender}`}
                    />
                  </ListItemButton>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          {!detail ? (
            <Card>
              <CardContent>
                <Typography sx={{ color: 'text.secondary' }}>Select a patient to view details.</Typography>
              </CardContent>
            </Card>
          ) : (
            <Stack spacing={2}>
              <Card>
                <CardContent>
                  <Typography sx={{ fontWeight: 900 }}>Patient details</Typography>
                  <Typography sx={{ color: 'text.secondary' }}>
                    {detail.patient.name} • {detail.patient.age} • {detail.patient.gender}
                  </Typography>

                  {detail.active_alert && (
                    <Box
                      sx={{
                        mt: 1.5,
                        p: 1.25,
                        borderRadius: 2,
                        background: 'rgba(211, 47, 47, 0.10)',
                        border: '1px solid rgba(211, 47, 47, 0.35)',
                        animation: 'mpPulse 1.2s ease-in-out infinite'
                      }}
                    >
                      <Stack direction="row" spacing={1} alignItems="center">
                        <WarningAmberRoundedIcon sx={{ color: 'error.main', animation: 'mpBlink 1s ease-in-out infinite' }} />
                        <Typography sx={{ fontWeight: 900, color: 'error.main' }}>
                          High Risk Detected – Immediate Medical Attention Required
                        </Typography>
                      </Stack>
                      <Typography sx={{ mt: 0.5, color: 'text.secondary' }}>
                        Risk: {detail.active_alert.risk_level} • {(detail.active_alert.probability * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  )}

                  <Typography sx={{ mt: 1 }}>
                    <b>Symptoms:</b> {(detail.patient.symptoms || []).join(', ') || '—'}
                  </Typography>
                  <Typography sx={{ mt: 0.5 }}>
                    <b>Vitals:</b> {JSON.stringify(detail.patient.vitals || {})}
                  </Typography>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography sx={{ fontWeight: 900 }}>AI predictions</Typography>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={async () => {
                        if (!selectedId) return
                        try {
                          await api.post('/predictions/run', { patient_id: selectedId, disease: 'heart' })
                          await api.post('/predictions/run', { patient_id: selectedId, disease: 'diabetes' })
                          await loadDetail(selectedId)
                          await refreshAlerts()
                          await refresh()
                          setToast({ open: true, msg: 'Predictions updated', sev: 'success' })
                        } catch (e: any) {
                          setToast({ open: true, msg: e?.response?.data?.detail || 'Prediction failed', sev: 'error' })
                        }
                      }}
                    >
                      Run Again
                    </Button>
                  </Stack>

                  <Divider sx={{ my: 1.5 }} />

                  <Stack spacing={2}>
                    {detail.predictions.map((pr) => {
                      const chartData = toChart(pr.feature_importance?.top || [])
                      return (
                        <Box key={pr.id}>
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Typography sx={{ fontWeight: 800 }}>{pr.disease.toUpperCase()}</Typography>
                            <RiskChip risk={pr.risk_level} prob={pr.probability} />
                          </Stack>

                          <Grid container spacing={2} sx={{ mt: 0.5 }}>
                            <Grid item xs={12} md={7}>
                              <Box sx={{ height: 160, borderRadius: 2, overflow: 'hidden' }}>
                                {chartData.length === 0 ? (
                                  <Box
                                    sx={{
                                      height: '100%',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      color: 'text.secondary',
                                      border: '1px dashed rgba(16, 24, 40, 0.18)',
                                      borderRadius: 2
                                    }}
                                  >
                                    Explainability chart will appear after model loads.
                                  </Box>
                                ) : (
                                  <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} margin={{ left: 6, right: 8 }}>
                                      <CartesianGrid strokeDasharray="3 3" />
                                      <XAxis dataKey="name" hide />
                                      <YAxis />
                                      <Tooltip />
                                      <Bar dataKey="impact" fill="#0bb3a9" radius={[8, 8, 0, 0]} />
                                    </BarChart>
                                  </ResponsiveContainer>
                                )}
                              </Box>
                            </Grid>

                            <Grid item xs={12} md={5}>
                              <Typography sx={{ color: 'text.secondary' }}>
                                <b>Tests:</b> {(pr.recommendations?.suggested_tests || []).join(', ')}
                              </Typography>
                              <Typography sx={{ color: 'text.secondary', mt: 0.5 }}>
                                <b>Specialist:</b> {(pr.recommendations?.suggested_specialists || []).join(', ')}
                              </Typography>

                              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                                <Button
                                  size="small"
                                  variant="contained"
                                  onClick={async () => {
                                    try {
                                      await api.post('/doctor/prediction/decision', {
                                        prediction_id: pr.id,
                                        doctor_note: note,
                                        doctor_decision: 'approved'
                                      })
                                      await loadDetail(selectedId!)
                                      setToast({ open: true, msg: 'Approved', sev: 'success' })
                                    } catch (e: any) {
                                      setToast({ open: true, msg: e?.response?.data?.detail || 'Approve failed', sev: 'error' })
                                    }
                                  }}
                                >
                                  Approve
                                </Button>
                                <Button
                                  size="small"
                                  variant="outlined"
                                  onClick={async () => {
                                    try {
                                      await api.post('/doctor/prediction/decision', {
                                        prediction_id: pr.id,
                                        doctor_note: note,
                                        doctor_decision: 'rejected'
                                      })
                                      await loadDetail(selectedId!)
                                      setToast({ open: true, msg: 'Rejected', sev: 'info' })
                                    } catch (e: any) {
                                      setToast({ open: true, msg: e?.response?.data?.detail || 'Reject failed', sev: 'error' })
                                    }
                                  }}
                                >
                                  Reject
                                </Button>
                                <Button
                                  size="small"
                                  variant="text"
                                  onClick={async () => {
                                    try {
                                      const r = await api.get(`/predictions/${pr.id}/report.pdf`, { responseType: 'blob' })
                                      downloadBlob(`MediPredict_${pr.disease}_${pr.id}.pdf`, r.data)
                                    } catch (e: any) {
                                      setToast({ open: true, msg: e?.response?.data?.detail || 'PDF download failed', sev: 'error' })
                                    }
                                  }}
                                >
                                  PDF
                                </Button>
                              </Stack>
                            </Grid>
                          </Grid>
                        </Box>
                      )
                    })}
                  </Stack>

                  <Divider sx={{ my: 1.5 }} />
                  <TextField label="Doctor notes" fullWidth multiline minRows={2} value={note} onChange={(e) => setNote(e.target.value)} />
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <Typography sx={{ fontWeight: 900, mb: 1 }}>Controlled AI assistant (safe)</Typography>
                  <Stack spacing={1}>
                    <TextField label="Ask" fullWidth value={chatMsg} onChange={(e) => setChatMsg(e.target.value)} />
                    <Stack direction="row" spacing={1}>
                      <Button
                        variant="contained"
                        onClick={async () => {
                          try {
                            const r = await api.post('/chat', { message: chatMsg, patient_id: selectedId })
                            setChatOut(r.data.response)
                          } catch (e: any) {
                            setToast({ open: true, msg: e?.response?.data?.detail || 'Chat failed', sev: 'error' })
                          }
                        }}
                      >
                        Send
                      </Button>
                      <Button variant="outlined" onClick={() => setChatOut('')}>
                        Clear
                      </Button>
                    </Stack>
                    {chatOut && (
                      <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f3f6ff', whiteSpace: 'pre-wrap' }}>{chatOut}</Box>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          )}
        </Grid>
      </Grid>
    </AppShell>
  )
}
