import MicRoundedIcon from '@mui/icons-material/MicRounded'
import MicOffRoundedIcon from '@mui/icons-material/MicOffRounded'
import WarningAmberRoundedIcon from '@mui/icons-material/WarningAmberRounded'
import { Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Grid, IconButton, MenuItem, Stack, TextField, Tooltip, Typography } from '@mui/material'
import { useMemo, useRef, useState } from 'react'
import AppShell from '../components/AppShell'
import { RiskChip } from '../components/RiskChip'
import { api } from '../api/client'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from 'recharts'

const SYMPTOMS = [
  'chest_pain',
  'shortness_of_breath',
  'fatigue',
  'headache',
  'dizziness',
  'nausea',
  'blurred_vision',
  'frequent_urination',
  'increased_thirst',
  'palpitations',
  'swelling_legs',
  'fever',
  'cough',
  'abdominal_pain'
]

type Prediction = {
  id: number
  disease: string
  risk_level: string
  probability: number
  alert_flag: boolean
  alert_id?: number | null
  feature_importance: { top: { feature: string; shap: number; value: number }[] }
  recommendations: any
}

function toChart(top: { feature: string; shap: number; value: number }[]) {
  return top.map((t) => ({ name: t.feature, impact: Math.abs(t.shap) }))
}

type SpeechRecognitionType = typeof window & {
  SpeechRecognition?: any
  webkitSpeechRecognition?: any
}

function getSpeechRecognitionCtor(): any | null {
  const w = window as unknown as SpeechRecognitionType
  return w.SpeechRecognition || w.webkitSpeechRecognition || null
}

function mapTranscriptToSymptoms(transcript: string): { matched: string[]; cleaned: string } {
  const t = transcript.toLowerCase()

  const rules: Array<{ keys: string[]; symptom: string }> = [
    { symptom: 'fever', keys: ['fever', 'temperature', 'high temp'] },
    { symptom: 'headache', keys: ['headache', 'head pain', 'migraine'] },
    { symptom: 'chest_pain', keys: ['chest pain', 'pain in chest', 'tightness in chest', 'chest tightness'] },
    { symptom: 'shortness_of_breath', keys: ['shortness of breath', 'breathless', 'difficulty breathing', 'hard to breathe'] },
    { symptom: 'cough', keys: ['cough', 'coughing'] },
    { symptom: 'fatigue', keys: ['fatigue', 'tired', 'weakness', 'low energy'] },
    { symptom: 'dizziness', keys: ['dizzy', 'dizziness', 'lightheaded'] },
    { symptom: 'nausea', keys: ['nausea', 'vomit', 'vomiting', 'queasy'] },
    { symptom: 'blurred_vision', keys: ['blurred vision', 'blurry vision', 'vision blur'] },
    { symptom: 'frequent_urination', keys: ['frequent urination', 'urinating frequently', 'pee often'] },
    { symptom: 'increased_thirst', keys: ['thirst', 'very thirsty', 'increased thirst'] },
    { symptom: 'palpitations', keys: ['palpitations', 'heart racing', 'fast heartbeat', 'pounding heart'] },
    { symptom: 'swelling_legs', keys: ['swollen legs', 'leg swelling', 'swelling in legs', 'ankle swelling'] },
    { symptom: 'abdominal_pain', keys: ['abdominal pain', 'stomach pain', 'belly pain', 'pain in abdomen'] }
  ]

  const matched = new Set<string>()
  for (const r of rules) {
    if (r.keys.some((k) => t.includes(k))) matched.add(r.symptom)
  }

  const cleaned = transcript
    .replace(/\s+/g, ' ')
    .trim()

  return { matched: Array.from(matched), cleaned }
}

export default function PatientDashboard() {
  const [name, setName] = useState('')
  const [age, setAge] = useState(45)
  const [gender, setGender] = useState<'male' | 'female'>('male')
  const [symptoms, setSymptoms] = useState<string[]>(['fatigue'])
  const [history, setHistory] = useState('')
  const [vitals, setVitals] = useState({ bp_systolic: 130, bp_diastolic: 85, heart_rate: 78, fasting_sugar: 120, bmi: 26.5, cholesterol: 210 })

  const [patientId, setPatientId] = useState<number | null>(null)
  const [preds, setPreds] = useState<Prediction[]>([])
  const [busy, setBusy] = useState(false)

  const highRisk = useMemo(() => preds.find((p) => p.alert_flag), [preds])
  const [alertOpen, setAlertOpen] = useState(false)

  // Voice input
  const speechCtor = useMemo(() => getSpeechRecognitionCtor(), [])
  const recognitionRef = useRef<any | null>(null)
  const [listening, setListening] = useState(false)
  const [processingVoice, setProcessingVoice] = useState(false)
  const [voiceCaptured, setVoiceCaptured] = useState<string>('')
  const [voiceMatched, setVoiceMatched] = useState<string[]>([])

  async function startVoice() {
    if (!speechCtor) {
      alert('Voice input is not supported in this browser. Try Chrome / Edge.')
      return
    }

    try {
      setVoiceCaptured('')
      setVoiceMatched([])

      const rec = new speechCtor()
      recognitionRef.current = rec

      rec.lang = 'en-US'
      rec.interimResults = true
      rec.continuous = false

      rec.onstart = () => {
        setListening(true)
      }

      rec.onerror = () => {
        setListening(false)
        setProcessingVoice(false)
        alert('Microphone permission denied or unavailable.')
      }

      rec.onresult = (event: any) => {
        const text = Array.from(event.results)
          .map((r: any) => r[0]?.transcript)
          .join(' ')
        setVoiceCaptured(text)
      }

      rec.onend = () => {
        setListening(false)
        setProcessingVoice(true)
        setTimeout(() => {
          const { matched, cleaned } = mapTranscriptToSymptoms(voiceCaptured)
          setVoiceMatched(matched)
          if (matched.length > 0) {
            const next = Array.from(new Set([...symptoms, ...matched]))
            setSymptoms(next)
          }
          setVoiceCaptured(cleaned)
          setProcessingVoice(false)
        }, 250)
      }

      rec.start()
    } catch {
      setListening(false)
      setProcessingVoice(false)
      alert('Unable to start voice input. Check microphone permissions.')
    }
  }

  function stopVoice() {
    try {
      recognitionRef.current?.stop?.()
    } catch {
      // ignore
    }
    setListening(false)
  }

  return (
    <AppShell title="Patient Dashboard">
      {highRisk && (
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
            High Risk Detected – Immediate Medical Attention Required
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Button size="small" variant="contained" color="error" onClick={() => setAlertOpen(true)}>
            View Alert
          </Button>
        </Box>
      )}

      <Dialog open={alertOpen} onClose={() => setAlertOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningAmberRoundedIcon color="error" /> Emergency Alert
        </DialogTitle>
        <DialogContent>
          {!highRisk ? (
            <Typography sx={{ color: 'text.secondary' }}>No critical alert.</Typography>
          ) : (
            <Stack spacing={1.2} sx={{ mt: 1 }}>
              <Typography>
                <b>Patient:</b> {name || '—'}
              </Typography>
              <Typography>
                <b>Risk:</b> {highRisk.risk_level} • {(highRisk.probability * 100).toFixed(0)}%
              </Typography>
              <Typography sx={{ mt: 1, color: 'text.secondary' }}>
                <b>Top contributing factors:</b>
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {(highRisk.feature_importance?.top || []).slice(0, 6).map((t) => (
                  <Chip key={t.feature} size="small" label={t.feature} />
                ))}
              </Stack>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            variant="contained"
            color="error"
            disabled={!highRisk || !patientId}
            onClick={async () => {
              if (!highRisk || !patientId) return
              await api.post('/alerts/notify', { patient_id: patientId, risk_level: highRisk.risk_level, probability: highRisk.probability })
              setAlertOpen(false)
            }}
          >
            Notify Doctor
          </Button>
          <Button
            variant="outlined"
            disabled={!highRisk}
            onClick={() => {
              if (!highRisk) return
              window.open(`${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/predictions/${highRisk.id}/report.pdf`, '_blank')
            }}
          >
            View Full Report
          </Button>
        </DialogActions>
      </Dialog>

      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                  <Typography sx={{ fontWeight: 900 }}>Patient intake</Typography>
                  <Stack direction="row" spacing={1}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={async () => {
                        const r = await api.get('/patients/simulate/case')
                        setName(r.data.name)
                        setAge(r.data.age)
                        setGender(r.data.gender)
                        setSymptoms(r.data.symptoms)
                        setVitals(r.data.vitals)
                        setHistory(r.data.medical_history)
                        setPatientId(null)
                        setPreds([])
                      }}
                    >
                      Simulate Patient Case
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      disabled={busy}
                      onClick={async () => {
                        setBusy(true)
                        try {
                          const r = await api.post('/patients', {
                            name,
                            age,
                            gender,
                            symptoms,
                            vitals,
                            medical_history: history
                          })
                          setPatientId(r.data.id)
                        } finally {
                          setBusy(false)
                        }
                      }}
                    >
                      Save Patient
                    </Button>
                  </Stack>
                </Stack>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField label="Name" fullWidth value={name} onChange={(e) => setName(e.target.value)} />
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <TextField label="Age" type="number" fullWidth value={age} onChange={(e) => setAge(Number(e.target.value))} />
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <TextField label="Gender" select fullWidth value={gender} onChange={(e) => setGender(e.target.value as any)}>
                      <MenuItem value="male">Male</MenuItem>
                      <MenuItem value="female">Female</MenuItem>
                    </TextField>
                  </Grid>

                  <Grid item xs={12}>
                    <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ mb: 0.5 }}>
                      <Typography sx={{ fontWeight: 800 }}>Symptoms</Typography>
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <Typography sx={{ fontSize: 12, color: 'text.secondary' }}>
                          {listening ? 'Listening...' : processingVoice ? 'Processing...' : voiceCaptured ? `Captured: ${voiceMatched.map((s) => s.replaceAll('_', ' ')).join(', ') || voiceCaptured}` : 'Voice input'}
                        </Typography>
                        <Tooltip title={speechCtor ? (listening ? 'Stop' : 'Use microphone') : 'Microphone not supported'}>
                          <span>
                            <IconButton
                              size="small"
                              color={listening ? 'error' : 'primary'}
                              disabled={!speechCtor}
                              onClick={() => (listening ? stopVoice() : startVoice())}
                            >
                              {listening ? <MicOffRoundedIcon /> : <MicRoundedIcon />}
                            </IconButton>
                          </span>
                        </Tooltip>
                      </Stack>
                    </Stack>

                    <TextField
                      label="Symptoms (multi-select)"
                      select
                      fullWidth
                      SelectProps={{ multiple: true, value: symptoms, onChange: (e) => setSymptoms(e.target.value as any) }}
                    >
                      {SYMPTOMS.map((s) => (
                        <MenuItem key={s} value={s}>
                          {s.replaceAll('_', ' ')}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField label="Medical history" fullWidth multiline minRows={2} value={history} onChange={(e) => setHistory(e.target.value)} />
                  </Grid>

                  {(
                    [
                      ['bp_systolic', 'BP Systolic'],
                      ['bp_diastolic', 'BP Diastolic'],
                      ['heart_rate', 'Heart rate'],
                      ['fasting_sugar', 'Fasting sugar'],
                      ['bmi', 'BMI'],
                      ['cholesterol', 'Cholesterol']
                    ] as const
                  ).map(([k, label]) => (
                    <Grid item xs={6} md={4} key={k}>
                      <TextField
                        label={label}
                        type="number"
                        fullWidth
                        value={(vitals as any)[k]}
                        onChange={(e) => setVitals((v) => ({ ...v, [k]: Number(e.target.value) }))}
                      />
                    </Grid>
                  ))}
                </Grid>

                <Divider />

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                  <Button
                    variant="contained"
                    disabled={!patientId || busy}
                    onClick={async () => {
                      if (!patientId) return
                      setBusy(true)
                      try {
                        const heart = await api.post('/predictions/run', { patient_id: patientId, disease: 'heart' })
                        const diab = await api.post('/predictions/run', { patient_id: patientId, disease: 'diabetes' })
                        const next = [heart.data, diab.data]
                        setPreds(next)
                        if (next.some((p: any) => p.alert_flag)) setAlertOpen(true)
                      } finally {
                        setBusy(false)
                      }
                    }}
                  >
                    Predict Risk
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={!patientId}
                    onClick={async () => {
                      if (!patientId) return
                      const file = (document.getElementById('reportUpload') as HTMLInputElement).files?.[0]
                      if (!file) return
                      const form = new FormData()
                      form.append('file', file)
                      await api.post(`/reports/upload/${patientId}`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
                      alert('Report uploaded')
                    }}
                  >
                    Upload report
                  </Button>
                  <input id="reportUpload" type="file" style={{ display: 'none' }} />
                  <Button variant="text" onClick={() => (document.getElementById('reportUpload') as HTMLInputElement).click()}>
                    Choose file
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Stack spacing={2}>
            <Card sx={{ overflow: 'hidden' }}>
              <CardContent>
                <Typography sx={{ fontWeight: 900, mb: 1 }}>Live prediction output</Typography>
                {preds.length === 0 ? (
                  <Typography sx={{ color: 'text.secondary' }}>Save a patient, then click “Predict Risk”.</Typography>
                ) : (
                  <Stack spacing={2}>
                    {preds.map((pr) => (
                      <Box key={pr.id}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography sx={{ fontWeight: 800 }}>{pr.disease.toUpperCase()}</Typography>
                          <RiskChip risk={pr.risk_level} prob={pr.probability} />
                        </Stack>
                        <Box sx={{ height: 180, mt: 1 }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={toChart(pr.feature_importance?.top || [])} margin={{ left: 10, right: 10 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" hide />
                              <YAxis />
                              <RTooltip />
                              <Bar dataKey="impact" fill="#0b5cff" radius={[8, 8, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </Box>
                        <Typography sx={{ mt: 1, color: 'text.secondary' }}>Top drivers:</Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 0.5 }}>
                          {(pr.feature_importance?.top || []).slice(0, 6).map((t) => (
                            <Chip key={t.feature} size="small" label={`${t.feature}`} />
                          ))}
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                )}
              </CardContent>
            </Card>

            <Card sx={{ overflow: 'hidden' }}>
              <CardContent>
                <Typography sx={{ fontWeight: 900, mb: 1 }}>Actionable recommendations</Typography>
                {preds.length === 0 ? (
                  <Typography sx={{ color: 'text.secondary' }}>Recommendations appear after prediction.</Typography>
                ) : (
                  <Stack spacing={1}>
                    {preds.map((pr) => (
                      <Box key={pr.id}>
                        <Typography sx={{ fontWeight: 800 }}>{pr.disease.toUpperCase()}</Typography>
                        <Typography sx={{ color: 'text.secondary' }}>Tests: {(pr.recommendations?.suggested_tests || []).join(', ')}</Typography>
                        <Typography sx={{ color: 'text.secondary' }}>Specialist: {(pr.recommendations?.suggested_specialists || []).join(', ')}</Typography>
                      </Box>
                    ))}
                  </Stack>
                )}
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </AppShell>
  )
}
