import { Chip } from '@mui/material'

export function RiskChip({ risk, prob }: { risk: string; prob?: number }) {
  const color = risk === 'High' ? 'error' : risk === 'Medium' ? 'warning' : 'success'
  const label = prob === undefined ? risk : `${risk} • ${(prob * 100).toFixed(0)}%`
  return <Chip size="small" color={color as any} label={label} />
}
