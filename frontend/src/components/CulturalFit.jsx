import { useState } from 'react'
import PropTypes from 'prop-types'

// ── helpers ───────────────────────────────────────────────────────────────────

function scoreColor(score) {
  if (score > 65) return '#4DBBAA'
  if (score >= 40) return '#C9A84C'
  return '#C46B8A'
}

function barColor(score, theme) {
  if (score > 70) return '#C46B8A'         // warm pink — high score
  if (score >= 40) return theme.accentActive // mid score
  return '#7C6FCD'                          // muted purple — low score
}

// ── skeleton ──────────────────────────────────────────────────────────────────

function SkeletonBar({ theme }) {
  const pulse = {
    background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.bgCard} 50%, ${theme.borderDefault} 75%)`,
    backgroundSize: '200% 100%',
    animation: 'skeleton-pulse 1.4s ease-in-out infinite',
    borderRadius: 4,
  }
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <div style={{ ...pulse, width: '40%', height: 10 }} />
        <div style={{ ...pulse, width: 24, height: 10 }} />
      </div>
      <div style={{ ...pulse, width: '100%', height: 4, borderRadius: 2 }} />
    </div>
  )
}

// ── dimension bar row ─────────────────────────────────────────────────────────

function DimensionBar({ dim, theme }) {
  const [hovered, setHovered] = useState(false)
  const score = dim.score ?? 0
  const fillColor = barColor(score, theme)

  return (
    <div
      style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
        <span style={{ fontSize: 10, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {dim.dimension_name || dim.dimension}
        </span>
        <span style={{ fontSize: 10, color: theme.textSecondary }}>{score}</span>
      </div>
      <div style={{ width: '100%', height: 4, background: theme.borderDefault, borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: `${Math.max(0, Math.min(100, score))}%`, height: '100%', background: fillColor, borderRadius: 2 }} />
      </div>

      {/* implication shown only on hover, as a tooltip positioned above the row */}
      {hovered && dim.implication && (
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: 0,
          marginBottom: 6,
          background: theme.bgCard,
          border: `1px solid ${theme.borderDefault}`,
          borderRadius: 6,
          padding: 8,
          fontSize: 11,
          color: theme.textSecondary,
          maxWidth: 240,
          zIndex: 10,
        }}>
          {dim.implication}
        </div>
      )}
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function CulturalFit({ agent3Output, theme }) {
  const hasData = agent3Output && Object.keys(agent3Output).length > 0
  const score = agent3Output?.fit_score
  const label = agent3Output?.score_label
  const dimensions = agent3Output?.dimension_analysis || []

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
      <style>{`
        @keyframes skeleton-pulse {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>

      <p style={{
        fontSize: 10, fontWeight: 500, letterSpacing: '0.1em',
        color: theme.textMuted, textTransform: 'uppercase', margin: '0 0 20px',
      }}>
        CULTURAL FIT
      </p>

      {!hasData ? (
        <>
          <div style={{
            background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.bgCard} 50%, ${theme.borderDefault} 75%)`,
            backgroundSize: '200% 100%',
            animation: 'skeleton-pulse 1.4s ease-in-out infinite',
            borderRadius: 4, width: '50%', height: 48, margin: '0 auto 8px',
          }} />
          <div style={{
            background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.bgCard} 50%, ${theme.borderDefault} 75%)`,
            backgroundSize: '200% 100%',
            animation: 'skeleton-pulse 1.4s ease-in-out infinite',
            borderRadius: 4, width: '35%', height: 13, margin: '0 auto 20px',
          }} />
          {Array.from({ length: 6 }, (_, i) => <SkeletonBar key={i} theme={theme} />)}
        </>
      ) : (
        <>
          {score != null && (
            <p style={{
              fontSize: 56, fontWeight: 600, textAlign: 'center', lineHeight: 1,
              color: scoreColor(score), margin: 0,
            }}>
              {score}
            </p>
          )}
          {label && (
            <p style={{ fontSize: 13, color: theme.textSecondary, textAlign: 'center', margin: '4px 0 20px' }}>
              {label}
            </p>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
            {dimensions.slice(0, 6).map((dim, i) => (
              <DimensionBar key={i} dim={dim} theme={theme} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

CulturalFit.propTypes = {
  agent3Output: PropTypes.object,
  theme:        PropTypes.object.isRequired,
}
