import PropTypes from 'prop-types'
import {
  ResponsiveContainer,
  RadarChart as ReRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

// ── constants ─────────────────────────────────────────────────────────────────

const AXES = [
  'Market growth',
  'Cultural fit',
  'Internet penetration',
  'Political stability',
  'Ease of business',
  'Corruption index',
]

// ── main component ────────────────────────────────────────────────────────────

export default function RadarChart({ radarScores, theme }) {
  const hasData = radarScores && Object.keys(radarScores).length > 0

  // Build a normalized lookup (lowercased, trimmed keys) so minor key
  // formatting differences from the backend (casing/whitespace) don't
  // cause a score to fall through to 0.
  const normalizedScores = {}
  if (radarScores) {
    Object.keys(radarScores).forEach((k) => {
      normalizedScores[k.trim().toLowerCase()] = radarScores[k]
    })
  }

  const data = AXES.map((key) => {
    const raw = radarScores?.[key] ?? normalizedScores[key.trim().toLowerCase()]
    return {
      subject: key,
      score: typeof raw === 'number' ? raw : Number(raw) || 0,
      ideal: 80,
    }
  })

  // Verify all 6 signals are present in the transformed data array
  console.log('RadarChart transformed data:', data)

  return (
    <div style={{
      background: theme.bgCard,
      border: `1px solid ${theme.borderDefault}`,
      borderRadius: 12,
      padding: 20,
      height: '100%',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <p style={{
        fontSize: 10, fontWeight: 500, letterSpacing: '0.1em',
        color: theme.textMuted, textTransform: 'uppercase', margin: '0 0 16px',
      }}>
        SIGNAL RADAR
      </p>

      {!hasData ? (
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 13, color: theme.textMuted,
        }}>
          Awaiting simulation data
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={380}>
            <ReRadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <PolarGrid gridType="polygon" stroke={theme.borderDefault} strokeOpacity={0.6} />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fontSize: 10, fill: theme.textSecondary, fontFamily: 'inherit' }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fontSize: 9, fill: theme.textMuted }}
                tickCount={4}
                axisLine={false}
              />
              <Radar
                name="Market signals"
                dataKey="score"
                stroke={theme.accentActive}
                strokeWidth={1.5}
                fill={theme.accentActive}
                fillOpacity={0.28}
                dot={{ r: 3, fill: theme.accentActive }}
                label={(props) => {
                  const { x, y, value, cx, cy } = props
                  // push the label outward from the chart center so it sits outside the polygon vertex
                  const dx = x - cx
                  const dy = y - cy
                  const len = Math.sqrt(dx * dx + dy * dy) || 1
                  const offset = 12
                  const lx = x + (dx / len) * offset
                  const ly = y + (dy / len) * offset
                  return (
                    <text
                      x={lx}
                      y={ly}
                      fontSize={10}
                      fontWeight={500}
                      fill={theme.textSecondary}
                      textAnchor="middle"
                      dominantBaseline="central"
                    >
                      {value}
                    </text>
                  )
                }}
              />
              <Radar
                name="Ideal"
                dataKey="ideal"
                stroke={theme.borderStrong}
                strokeWidth={1}
                strokeDasharray="3 3"
                fill="none"
                dot={false}
              />
            </ReRadarChart>
          </ResponsiveContainer>

          {/* ── Legend ── */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: 20,
            marginTop: 12, paddingTop: 12, borderTop: `1px solid ${theme.borderDefault}`,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: theme.accentActive, display: 'inline-block' }} />
              <span style={{ fontSize: 11, color: theme.textSecondary }}>Market signals</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{
                width: 16, height: 0, borderTop: `1px dashed ${theme.borderStrong}`,
                display: 'inline-block',
              }} />
              <span style={{ fontSize: 11, color: theme.textMuted }}>Ideal (80)</span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

RadarChart.propTypes = {
  radarScores: PropTypes.object,
  theme:       PropTypes.object.isRequired,
}

// ── demo wrapper for isolated testing ─────────────────────────────────────────

const DEMO_SCORES = {
  'Market growth': 68,
  'Cultural fit': 52,
  'Internet penetration': 84,
  'Political stability': 40,
  'Ease of business': 35,
  'Corruption index': 38,
}

export function RadarChartDemo({ theme }) {
  return <RadarChart radarScores={DEMO_SCORES} theme={theme} />
}

RadarChartDemo.propTypes = {
  theme: PropTypes.object.isRequired,
}
