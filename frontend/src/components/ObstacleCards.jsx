import { useState } from 'react'
import PropTypes from 'prop-types'

// ── severity config ───────────────────────────────────────────────────────────

const SEVERITY = {
  Critical: { text: '#C46B8A', bg: 'rgba(196,107,138,0.15)', tint: 'rgba(196,107,138,0.04)', border: 'rgba(196,107,138,0.20)' },
  High:     { text: '#D4845A', bg: 'rgba(212,132,90,0.15)',  tint: 'rgba(212,132,90,0.04)',  border: 'rgba(212,132,90,0.20)'  },
  Medium:   { text: '#C9A84C', bg: 'rgba(201,168,76,0.15)',  tint: 'rgba(201,168,76,0.04)',  border: 'rgba(201,168,76,0.20)'  },
  Low:      { text: '#4DBBAA', bg: 'rgba(77,187,170,0.15)',  tint: 'rgba(77,187,170,0.04)',  border: 'rgba(77,187,170,0.20)'  },
}

function sv(level) {
  return SEVERITY[level] ?? SEVERITY.Low
}

// ── skeleton card ─────────────────────────────────────────────────────────────

function SkeletonCard({ theme }) {
  const pulse = {
    background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.borderStrong} 50%, ${theme.borderDefault} 75%)`,
    backgroundSize: '200% 100%',
    animation: 'skeleton-pulse 1.4s ease-in-out infinite',
    borderRadius: 4,
  }
  return (
    <div style={{
      background: theme.bgCard, border: `1px solid ${theme.borderDefault}`,
      borderRadius: 10, padding: '14px 12px', marginBottom: 8,
      minHeight: 80, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 10,
    }}>
      <div style={{ ...pulse, width: 60, height: 18, borderRadius: 12 }} />
      <div style={{ ...pulse, width: '80%', height: 13 }} />
    </div>
  )
}

// ── detail overlay ────────────────────────────────────────────────────────────

function ObstacleOverlay({ obstacle, theme, onClose }) {
  const s = sv(obstacle.severity)
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: theme.bgCard,
      border: `1px solid ${theme.borderDefault}`,
      borderRadius: 12,
      padding: '1.5rem',
      overflowY: 'auto',
      zIndex: 10,
      animation: 'slide-in-right 0.22s ease',
    }}>
      {/* header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <div style={{ flex: 1, paddingRight: 10 }}>
          <div style={{ display: 'flex', gap: 7, alignItems: 'center', marginBottom: 8 }}>
            <span style={{
              background: s.bg, color: s.text,
              fontSize: 10, fontWeight: 600,
              padding: '2px 10px', borderRadius: 12,
            }}>
              {obstacle.severity}
            </span>
            {obstacle.category && (
              <span style={{ fontSize: 10, color: theme.textMuted }}>{obstacle.category}</span>
            )}
          </div>
          <p style={{ fontSize: 14, fontWeight: 700, color: theme.textPrimary, margin: 0, lineHeight: 1.35 }}>
            {obstacle.title}
          </p>
        </div>
        <button onClick={onClose} style={{
          background: theme.borderDefault, border: 'none', borderRadius: '50%',
          width: 24, height: 24, cursor: 'pointer', color: theme.textSecondary,
          fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>×</button>
      </div>

      {[
        { label: 'Description',          value: obstacle.description },
        { label: 'Mitigation',           value: obstacle.mitigation },
        { label: 'Time sensitivity',     value: obstacle.time_sensitivity },
        { label: 'Cost to fix',          value: obstacle.cost_to_fix },
        { label: 'Early warning signal', value: obstacle.early_warning_signal },
      ].map(({ label, value }) => value && (
        <div key={label} style={{ marginBottom: 12 }}>
          <p style={{ fontSize: 10, fontWeight: 600, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.09em', margin: '0 0 3px' }}>{label}</p>
          <p style={{ fontSize: 12, color: theme.textSecondary, margin: 0, lineHeight: 1.55 }}>{value}</p>
        </div>
      ))}
    </div>
  )
}

// ── mini card ─────────────────────────────────────────────────────────────────

function ObstacleMiniCard({ obstacle, theme, onClick }) {
  const [hovered, setHovered] = useState(false)
  const s = sv(obstacle.severity)

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: theme.bgCard,
        border: `1px solid ${hovered ? theme.borderStrong : theme.borderDefault}`,
        borderRadius: 10,
        padding: '14px 12px',
        marginBottom: 8,
        cursor: 'pointer',
        minHeight: 80,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        transition: 'border-color 0.15s',
        boxSizing: 'border-box',
        width: '100%',
      }}
    >
      {/* severity pill */}
      <span style={{
        background: s.bg, color: s.text,
        fontSize: 10, fontWeight: 500,
        padding: '2px 10px', borderRadius: 12,
        display: 'inline-block',
      }}>
        {obstacle.severity}
      </span>

      {/* title */}
      <p style={{
        fontSize: 13, fontWeight: 600, color: theme.textPrimary,
        margin: '8px 0 0', lineHeight: 1.4,
        display: '-webkit-box', WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical', overflow: 'hidden',
        wordBreak: 'break-word', overflowWrap: 'break-word',
        width: '100%',
      }}>
        {obstacle.title}
      </p>
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function ObstacleCards({ obstacles, theme }) {
  const [openIndex, setOpenIndex] = useState(null)
  const list = obstacles && obstacles.length > 0 ? obstacles : null

  return (
    <div style={{ position: 'relative', height: '100%', overflow: 'hidden', width: '100%', maxWidth: '100%', minWidth: 0, overflowX: 'hidden', boxSizing: 'border-box' }}>
      <style>{`
        @keyframes slide-in-right {
          from { opacity: 0; transform: translateX(14px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes skeleton-pulse {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>

      {list
        ? list.map((obstacle, i) => (
            <ObstacleMiniCard key={i} obstacle={obstacle} theme={theme} onClick={() => setOpenIndex(i)} />
          ))
        : Array.from({ length: 5 }, (_, i) => <SkeletonCard key={i} theme={theme} />)
      }

      {openIndex !== null && list && (
        <ObstacleOverlay
          obstacle={list[openIndex]}
          theme={theme}
          onClose={() => setOpenIndex(null)}
        />
      )}
    </div>
  )
}

ObstacleCards.propTypes = {
  obstacles: PropTypes.array,
  theme:     PropTypes.object.isRequired,
}
