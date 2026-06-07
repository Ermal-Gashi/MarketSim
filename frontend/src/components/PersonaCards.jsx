import { useState } from 'react'
import PropTypes from 'prop-types'

// ── helpers ───────────────────────────────────────────────────────────────────

function likelihoodColor(level, theme) {
  if (level === 'High')   return theme.accentActive
  if (level === 'Medium') return '#C9A84C'
  return '#C46B8A'
}

// ── avatar silhouette ─────────────────────────────────────────────────────────

function AvatarBlock({ theme }) {
  return (
    <div style={{
      width: 52, height: 52, borderRadius: 8,
      background: theme.borderDefault,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0,
    }}>
      <svg width="26" height="30" viewBox="0 0 26 30" fill="none">
        {/* head */}
        <circle cx="13" cy="9" r="7" fill={theme.textMuted} />
        {/* body */}
        <rect x="4" y="19" width="18" height="11" rx="5" fill={theme.textMuted} />
      </svg>
    </div>
  )
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
      borderRadius: 10, padding: 12, flex: 1,
      display: 'flex', alignItems: 'center', gap: 10, minHeight: 80,
    }}>
      <div style={{ ...pulse, width: 52, height: 52, borderRadius: 8, flexShrink: 0 }} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
        <div style={{ ...pulse, width: '65%', height: 13 }} />
        <div style={{ ...pulse, width: '45%', height: 11 }} />
      </div>
    </div>
  )
}

// ── detail overlay ────────────────────────────────────────────────────────────

function PersonaOverlay({ persona, theme, onClose }) {
  const dotColor = likelihoodColor(persona.purchase_likelihood, theme)
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: theme.bgCard,
      border: `1px solid ${theme.borderDefault}`,
      borderRadius: 12,
      padding: '1.5rem',
      overflowY: 'auto',
      zIndex: 10,
      animation: 'slide-in-left 0.22s ease',
    }}>
      {/* header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
            <p style={{ fontSize: 15, fontWeight: 700, color: theme.textPrimary, margin: 0 }}>
              {persona.name}{persona.age ? `, ${persona.age}` : ''}
            </p>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: dotColor, display: 'inline-block', flexShrink: 0,
            }} />
          </div>
          {persona.archetype_label && (
            <p style={{ fontSize: 10, color: theme.accentActive, textTransform: 'uppercase', letterSpacing: '0.1em', margin: '0 0 2px', fontWeight: 500 }}>
              {persona.archetype_label}
            </p>
          )}
          {persona.job_title && (
            <p style={{ fontSize: 11, color: theme.textSecondary, margin: '0 0 1px' }}>{persona.job_title}</p>
          )}
          {persona.city && (
            <p style={{ fontSize: 10, color: theme.textMuted, margin: 0 }}>{persona.city}</p>
          )}
        </div>
        <button onClick={onClose} style={{
          background: theme.borderDefault, border: 'none', borderRadius: '50%',
          width: 24, height: 24, cursor: 'pointer', color: theme.textSecondary,
          fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>×</button>
      </div>

      {[
        { label: 'Why they buy',      value: persona.why_they_buy },
        { label: 'What stops them',   value: persona.what_stops_them },
        { label: 'How they discover', value: persona.how_they_discover },
      ].map(({ label, value }) => value && (
        <div key={label} style={{ marginBottom: 12 }}>
          <p style={{ fontSize: 10, fontWeight: 600, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.09em', margin: '0 0 3px' }}>{label}</p>
          <p style={{ fontSize: 12, color: theme.textSecondary, margin: 0, lineHeight: 1.55 }}>{value}</p>
        </div>
      ))}

      {persona.variance_profile && (
        <div style={{ marginTop: 10, padding: '10px 12px', background: theme.bgPage, borderRadius: 8, border: `1px solid ${theme.borderDefault}` }}>
          <p style={{ fontSize: 10, fontWeight: 600, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.09em', margin: '0 0 8px' }}>Variance Profile</p>
          {[
            { label: 'Conversion range', value: persona.variance_profile.conversion_range },
            { label: 'Tips to High',     value: persona.variance_profile.tipping_point_to_high },
            { label: 'Tips to Low',      value: persona.variance_profile.tipping_point_to_low },
          ].map(({ label, value }) => value && (
            <div key={label} style={{ display: 'flex', gap: 8, marginBottom: 5 }}>
              <span style={{ fontSize: 10, color: theme.textMuted, minWidth: 110, flexShrink: 0 }}>{label}:</span>
              <span style={{ fontSize: 10, color: theme.textSecondary, lineHeight: 1.4 }}>{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── mini card ─────────────────────────────────────────────────────────────────

function PersonaMiniCard({ persona, theme, onClick, onArchetypeHover }) {
  const [hovered, setHovered] = useState(false)
  const dotColor = likelihoodColor(persona.purchase_likelihood, theme)

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => { setHovered(true); onArchetypeHover && onArchetypeHover(persona.archetype_name || null) }}
      onMouseLeave={() => { setHovered(false); onArchetypeHover && onArchetypeHover(null) }}
      style={{
        position: 'relative',
        background: theme.bgCard,
        border: `1px solid ${hovered ? theme.borderStrong : theme.borderDefault}`,
        borderRadius: 10,
        padding: 12,
        flex: 1,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        minHeight: 80,
        transition: 'border-color 0.15s',
      }}
    >
      <AvatarBlock theme={theme} />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <p style={{ fontSize: 13, fontWeight: 600, color: theme.textPrimary, margin: 0 }}>
          {persona.name}{persona.age ? `, ${persona.age}` : ''}
        </p>
        <p style={{ fontSize: 11, color: theme.textSecondary, margin: 0 }}>
          {persona.city}
        </p>
      </div>
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function PersonaCards({ personas, theme, onArchetypeHover }) {
  const [openIndex, setOpenIndex] = useState(null)
  const list = personas && personas.length > 0 ? personas : null

  return (
    <div style={{ position: 'relative', height: '100%', width: '100%', maxWidth: '100%', overflowX: 'hidden', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <style>{`
        @keyframes slide-in-left {
          from { opacity: 0; transform: translateX(-14px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes skeleton-pulse {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>

      {list
        ? list.map((persona, i) => (
            <PersonaMiniCard key={i} persona={persona} theme={theme} onClick={() => setOpenIndex(i)} onArchetypeHover={onArchetypeHover} />
          ))
        : Array.from({ length: 5 }, (_, i) => <SkeletonCard key={i} theme={theme} />)
      }

      {openIndex !== null && list && (
        <PersonaOverlay
          persona={list[openIndex]}
          theme={theme}
          onClose={() => setOpenIndex(null)}
        />
      )}
    </div>
  )
}

PersonaCards.propTypes = {
  personas:         PropTypes.array,
  theme:            PropTypes.object.isRequired,
  onArchetypeHover: PropTypes.func,
}
