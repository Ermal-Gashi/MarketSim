import { useState } from 'react'
import PropTypes from 'prop-types'

// ── label helper ──────────────────────────────────────────────────────────────

function CardLabel({ children, theme, marginBottom = 10 }) {
  return (
    <p style={{
      fontSize: 10, fontWeight: 500, letterSpacing: '0.1em',
      color: theme.textSecondary, textTransform: 'uppercase', margin: `0 0 ${marginBottom}px`,
    }}>
      {children}
    </p>
  )
}

// ── inline icons (no icon library installed — simple SVGs sized/colored per spec) ──

function AlertTriangleIcon({ size = 18, color }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  )
}

function RefreshIcon({ size = 18, color }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  )
}

// ── generate report button (verdict-stamp style) ─────────────────────────────

function GenerateReportButton({ theme }) {
  const [hovered, setHovered] = useState(false)

  return (
    <>
      <style>{`
        @keyframes report-btn-pulse {
          0%   { box-shadow: 0 0 0 0 rgba(77,187,170,0.4); }
          100% { box-shadow: 0 0 0 12px rgba(77,187,170,0); }
        }
      `}</style>
      <div
        onClick={() => console.log('Generate report clicked')}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          position: 'relative',
          display: 'inline-flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '36px 56px',
          cursor: 'pointer',
          border: `2px solid ${hovered ? 'rgba(77,187,170,1)' : '#4DBBAA'}`,
          borderRadius: 4,
          background: hovered ? 'rgba(77,187,170,0.05)' : 'transparent',
          animation: 'report-btn-pulse 2s infinite ease-out',
          transition: 'border-color 0.2s, background 0.2s',
        }}
      >
        <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '0.25em', color: '#4DBBAA', textAlign: 'center' }}>
          GENERATE REPORT
        </span>
        <span style={{ fontSize: 12, color: theme.textSecondary, marginTop: 6, letterSpacing: '0.05em' }}>
          Export full PDF analysis
        </span>
      </div>
    </>
  )
}

// ── skeleton helpers ──────────────────────────────────────────────────────────

function pulseStyle(theme) {
  return {
    background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.bgCard} 50%, ${theme.borderDefault} 75%)`,
    backgroundSize: '200% 100%',
    animation: 'skeleton-pulse 1.4s ease-in-out infinite',
    borderRadius: 4,
  }
}

function SkeletonChip({ theme }) {
  const p = pulseStyle(theme)
  return (
    <div style={{
      background: theme.bgCard, border: `1px solid ${theme.borderDefault}`,
      borderRadius: 10, padding: '12px 16px',
      display: 'flex', flexDirection: 'column', gap: 4,
    }}>
      <div style={{ ...p, width: '50%', height: 9 }} />
      <div style={{ ...p, width: '65%', height: 20 }} />
    </div>
  )
}

function SkeletonCard({ theme, lines = 3 }) {
  const cardStyle = {
    background: theme.bgCard, border: `1px solid ${theme.borderDefault}`,
    borderRadius: 12, padding: 20, height: '100%', boxSizing: 'border-box',
    display: 'flex', flexDirection: 'column', gap: 10,
  }
  const p = pulseStyle(theme)
  return (
    <div style={cardStyle}>
      <div style={{ ...p, width: '40%', height: 10 }} />
      {Array.from({ length: lines }, (_, i) => (
        <div key={i} style={{ ...p, width: `${85 - i * 12}%`, height: 14 }} />
      ))}
    </div>
  )
}

// ── helpers ───────────────────────────────────────────────────────────────────

function truncate(text, max) {
  if (typeof text !== 'string') return text
  return text.length > max ? `${text.slice(0, max - 1).trimEnd()}…` : text
}

// ── main component ────────────────────────────────────────────────────────────

export default function BottomStrip({ agent6Output, agent3Output, agent2Output, theme }) {
  const has6 = agent6Output && Object.keys(agent6Output).length > 0
  const has3 = agent3Output && Object.keys(agent3Output).length > 0
  const has2 = agent2Output && Object.keys(agent2Output).length > 0

  const cardBase = {
    background: theme.bgCard,
    border: `1px solid ${theme.borderDefault}`,
    borderRadius: 12,
    padding: 20,
    height: '100%',
    boxSizing: 'border-box',
  }

  const competitors = (agent2Output?.major_local_competitors || []).slice(0, 6)
  const salesMotion = agent3Output?.sales_motion_recommendation
    ? agent3Output.sales_motion_recommendation.split(':')[0]
    : 'Hybrid'

  const chips = [
    { label: 'Confidence',       value: agent6Output?.confidence_score != null ? `${agent6Output.confidence_score}%` : '—' },
    { label: 'Time to revenue',  value: agent6Output?.time_to_first_revenue || '—' },
    { label: 'Est. CAC',         value: agent6Output?.estimated_cac || '—' },
    { label: 'Sales motion',     value: salesMotion },
  ]

  return (
    <div style={{ width: '100%', boxSizing: 'border-box' }}>
      <style>{`
        @keyframes skeleton-pulse {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>

      {/* ── Top stat strip — 4 chips ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0,1fr))', gap: 10, marginBottom: 12 }}>
        {!has6 ? (
          Array.from({ length: 4 }, (_, i) => <SkeletonChip key={i} theme={theme} />)
        ) : (
          chips.map(({ label, value }) => (
            <div key={label} style={{
              background: theme.bgCard, border: `1px solid ${theme.borderDefault}`,
              borderRadius: 10, padding: '12px 16px',
              display: 'flex', flexDirection: 'column', gap: 4,
            }}>
              <span style={{ fontSize: 10, fontWeight: 500, letterSpacing: '0.08em', textTransform: 'uppercase', color: theme.textSecondary }}>
                {label}
              </span>
              <span style={{ fontSize: 22, fontWeight: 500, color: theme.textPrimary }}>
                {value}
              </span>
            </div>
          ))
        )}
      </div>

      {/* ── Three columns ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 10, alignItems: 'stretch' }}>

        {/* ── Column 1 — First Move ── */}
        {!has6 ? (
          <SkeletonCard theme={theme} lines={3} />
        ) : (
          <div style={{
            ...cardBase,
            borderLeft: '3px solid #4DBBAA',
            borderRadius: '0 12px 12px 0',
          }}>
            <CardLabel theme={theme}>RECOMMENDED FIRST MOVE</CardLabel>
            <p style={{ fontSize: 16, fontWeight: 500, color: theme.textPrimary, lineHeight: 1.65, margin: '0 0 12px' }}>
              {agent6Output.recommended_first_move}
            </p>
            <span style={{
              fontSize: 10, background: 'rgba(77,187,170,0.15)', color: '#4DBBAA',
              padding: '2px 10px', borderRadius: 4, fontWeight: 500, display: 'inline-block',
            }}>
              Immediate action
            </span>

            {/* ── Wildcard + revisit mini cards (moved from former center column) ── */}
            <div style={{ borderTop: `1px solid ${theme.borderDefault}`, marginTop: 14, paddingTop: 14 }}>

              {/* wildcard mini card */}
              <div style={{
                background: 'rgba(201,168,76,0.06)',
                border: '1px solid rgba(201,168,76,0.2)',
                borderRadius: 8,
                padding: '10px 12px',
                marginBottom: 8,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <AlertTriangleIcon size={14} color="#C9A84C" />
                  <span style={{ fontSize: 9, fontWeight: 500, color: '#C9A84C', letterSpacing: '0.08em' }}>
                    WILDCARD
                  </span>
                </div>
                <p style={{ fontSize: 12, color: theme.textPrimary, lineHeight: 1.5, margin: '5px 0 0' }}>
                  {agent6Output.biggest_wildcard}
                </p>
              </div>

              {/* revisit mini card */}
              <div style={{
                background: 'rgba(124,111,205,0.06)',
                border: '1px solid rgba(124,111,205,0.2)',
                borderRadius: 8,
                padding: '10px 12px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <RefreshIcon size={14} color="#7C6FCD" />
                  <span style={{ fontSize: 9, fontWeight: 500, color: '#7C6FCD', letterSpacing: '0.08em' }}>
                    REVISIT IF
                  </span>
                </div>
                <p style={{ fontSize: 12, color: theme.textPrimary, lineHeight: 1.5, margin: '5px 0 0' }}>
                  {agent6Output.revisit_trigger}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── Column 2 — Generate Report button ── */}
        {!has6 ? (
          <SkeletonCard theme={theme} lines={3} />
        ) : (
          <div style={{
            background: 'transparent',
            border: 'none',
            height: '100%',
            boxSizing: 'border-box',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            <GenerateReportButton theme={theme} />
          </div>
        )}

        {/* ── Column 3 — Competitors ── */}
        {!has2 ? (
          <SkeletonCard theme={theme} lines={4} />
        ) : (
          <div style={{ ...cardBase, display: 'flex', flexDirection: 'column' }}>
            <CardLabel theme={theme}>LOCAL COMPETITORS</CardLabel>
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              {competitors.map((comp, i) => {
                const text = typeof comp === 'string' ? comp : (comp?.name || JSON.stringify(comp))
                const sepIdx = text.indexOf(' — ')
                const name = sepIdx === -1 ? text : text.slice(0, sepIdx)
                const description = sepIdx === -1 ? null : text.slice(sepIdx + 3)
                const accentColor = i <= 1 ? '#C46B8A' : i <= 3 ? '#C9A84C' : theme.borderStrong
                return (
                  <div key={i} style={{
                    flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
                    borderBottom: `1px solid ${theme.borderDefault}`,
                    borderLeft: `2px solid ${accentColor}`, paddingLeft: '10px',
                  }}>
                    <span style={{ fontSize: 12, fontWeight: 500, color: theme.textPrimary }}>
                      {name}
                    </span>
                    {description && (
                      <span style={{ fontSize: 11, color: theme.textSecondary, lineHeight: 1.4, marginTop: 2 }}>
                        {truncate(description, 80)}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

BottomStrip.propTypes = {
  agent6Output: PropTypes.object,
  agent3Output: PropTypes.object,
  agent2Output: PropTypes.object,
  theme:        PropTypes.object.isRequired,
}
