import { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { motion, AnimatePresence } from 'framer-motion'

// ── constants ─────────────────────────────────────────────────────────────────

const PHASE_COLORS = ['#C46B8A', '#C9A84C', '#7C6FCD', '#4DBBAA']

function colorFor(index) {
  return PHASE_COLORS[index % PHASE_COLORS.length]
}

function hexToRgba(hex, alpha) {
  const h = hex.replace('#', '')
  const r = parseInt(h.substring(0, 2), 16)
  const g = parseInt(h.substring(2, 4), 16)
  const b = parseInt(h.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

// build a left-to-right gradient string proportional to the number of phases,
// always sampling from the 4-color base palette so colors stay consistent
// even when there are fewer than 4 phases
function buildGradient(count) {
  if (count <= 1) return PHASE_COLORS[0]
  const stops = []
  for (let i = 0; i < count; i++) {
    const pct = (i / (count - 1)) * 100
    const colorIdx = Math.min(PHASE_COLORS.length - 1, Math.round((i / (count - 1)) * (PHASE_COLORS.length - 1)))
    stops.push(`${PHASE_COLORS[colorIdx]} ${pct}%`)
  }
  return `linear-gradient(90deg, ${stops.join(', ')})`
}

// ── phase popup ───────────────────────────────────────────────────────────────

function PhasePopup({ phase, color, theme, popupRef }) {
  return (
    <motion.div
      ref={popupRef}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 6 }}
      transition={{ duration: 0.2 }}
      style={{
        position: 'absolute',
        bottom: 'calc(100% + 12px)',
        left: '50%',
        transform: 'translateX(-50%)',
        background: theme.bgCard,
        border: `1px solid ${theme.borderDefault}`,
        borderRadius: 10,
        padding: 14,
        minWidth: 200,
        maxWidth: 260,
        zIndex: 50,
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      }}
    >
      {/* downward-pointing caret */}
      <div style={{
        position: 'absolute',
        bottom: -8,
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '8px solid transparent',
        borderRight: '8px solid transparent',
        borderTop: `8px solid ${theme.borderDefault}`,
      }} />

      <p style={{ margin: 0, fontSize: 12, fontWeight: 600, color: theme.textPrimary }}>
        {phase.phase_name}
      </p>
      <p style={{ margin: '2px 0 0', fontSize: 10, color: theme.textMuted }}>
        {phase.timeframe}
      </p>

      {Array.isArray(phase.actions) && phase.actions.length > 0 && (
        <ul style={{ marginTop: 8, paddingLeft: 0, listStyle: 'none' }}>
          {phase.actions.map((action, i) => (
            <li key={i} style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
              <span style={{
                width: 5, height: 5, borderRadius: '50%',
                background: color, flexShrink: 0, marginTop: 4,
              }} />
              <span style={{ fontSize: 11, color: theme.textSecondary, lineHeight: 1.5 }}>
                {action}
              </span>
            </li>
          ))}
        </ul>
      )}
    </motion.div>
  )
}

// ── phase node ────────────────────────────────────────────────────────────────

function PhaseNode({ phase, index, isActive, theme, onToggle, popupRef }) {
  const [hovered, setHovered] = useState(false)
  const color = colorFor(index)

  let background = hexToRgba(color, 0.2)
  let boxShadow = 'none'
  if (isActive) {
    background = hexToRgba(color, 0.3)
    boxShadow = `0 0 0 4px ${hexToRgba(color, 0.2)}`
  } else if (hovered) {
    background = hexToRgba(color, 0.35)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, position: 'relative' }}>
      {/* mask circle — same size as node, card-colored, sits between the line (z 0) and
          the node circle (z 2) so the line visually breaks/stops at each node */}
      <div style={{
        position: 'absolute',
        top: 0,
        width: 44,
        height: 44,
        borderRadius: '50%',
        background: theme.bgCard,
        zIndex: 1,
      }} />
      <div
        onClick={onToggle}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          width: 44,
          height: 44,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 14,
          fontWeight: 600,
          cursor: 'pointer',
          position: 'relative',
          zIndex: 2,
          transition: 'all 0.2s',
          background,
          border: `2px solid ${color}`,
          color,
          boxShadow,
          transform: hovered && !isActive ? 'scale(1.05)' : 'scale(1)',
        }}
      >
        {index + 1}
      </div>
      <p style={{
        fontSize: 12, fontWeight: 500, color: theme.textPrimary,
        margin: '10px 0 0', textAlign: 'center', maxWidth: 120,
      }}>
        {phase.phase_name}
      </p>
      <p style={{ fontSize: 10, color: theme.textMuted, margin: '3px 0 0', textAlign: 'center' }}>
        {phase.timeframe}
      </p>

      {/* floating popup positioned above this node */}
      <AnimatePresence>
        {isActive && (
          <PhasePopup phase={phase} color={color} theme={theme} popupRef={popupRef} />
        )}
      </AnimatePresence>
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function EntryRoadmap({ marketEntrySequence, theme }) {
  // no phase selected by default — popup hidden until a node is clicked
  const [activePhase, setActivePhase] = useState(null)
  const containerRef = useRef(null)
  const popupRef = useRef(null)

  // debug — verify the shape/contents of the prop arriving from ReportDashboard
  console.log('EntryRoadmap: marketEntrySequence:', marketEntrySequence)

  const hasData = Array.isArray(marketEntrySequence) && marketEntrySequence.length > 0

  // close popup when clicking anywhere outside the roadmap card / popup
  useEffect(() => {
    function handleOutsideClick(event) {
      const insideContainer = containerRef.current && containerRef.current.contains(event.target)
      const insidePopup = popupRef.current && popupRef.current.contains(event.target)
      if (!insideContainer && !insidePopup) {
        setActivePhase(null)
      } else if (insideContainer && !insidePopup) {
        // clicks inside the card but outside the popup are handled by node onClick toggles;
        // clicking empty card space should also dismiss the popup
        const clickedNode = event.target.closest && event.target.closest('[data-phase-node]')
        if (!clickedNode) setActivePhase(null)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  if (!hasData) {
    return (
      <div style={{
        background: theme.bgCard,
        border: `1px solid ${theme.borderDefault}`,
        borderRadius: 12,
        padding: 24,
        width: '100%',
        boxSizing: 'border-box',
        minHeight: 180,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 13,
        color: theme.textMuted,
      }}>
        Entry roadmap not available for this market
      </div>
    )
  }

  const count = marketEntrySequence.length
  // line spans from the center of the first node to the center of the last node
  const edgeInset = `calc(100% / ${count * 2})`

  return (
    <motion.div
      ref={containerRef}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      style={{
        background: theme.bgCard,
        border: `1px solid ${theme.borderDefault}`,
        borderRadius: 12,
        padding: 24,
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <p style={{
        fontSize: 10, fontWeight: 500, letterSpacing: '0.1em',
        color: theme.textMuted, textTransform: 'uppercase', margin: '0 0 28px',
      }}>
        ENTRY ROADMAP
      </p>

      {/* ── Timeline ── */}
      <div style={{ position: 'relative' }}>
        {/* connecting line — behind nodes (z-index 0), spans node-center to node-center */}
        <style>{`
          @keyframes travel {
            0%   { left: 5%; }
            100% { left: 95%; }
          }
        `}</style>
        <div style={{
          position: 'absolute',
          top: 22,
          left: edgeInset,
          right: edgeInset,
          height: 2,
          zIndex: 0,
        }}>
          {/* base gradient line */}
          <div style={{
            position: 'absolute',
            inset: 0,
            background: buildGradient(count),
            borderRadius: 1,
          }} />
          {/* traveling data-packet particle */}
          <div style={{
            position: 'absolute',
            top: '50%',
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.8)',
            boxShadow: '0 0 8px 2px rgba(255,255,255,0.5)',
            transform: 'translateY(-50%)',
            animation: 'travel 3s linear infinite',
          }} />
        </div>

        <div
          data-phase-node
          style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', position: 'relative', zIndex: 2 }}
        >
          {marketEntrySequence.map((phase, i) => (
            <PhaseNode
              key={i}
              phase={phase}
              index={i}
              isActive={activePhase === i}
              theme={theme}
              popupRef={popupRef}
              onToggle={() => setActivePhase((prev) => (prev === i ? null : i))}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

EntryRoadmap.propTypes = {
  marketEntrySequence: PropTypes.array,
  theme:               PropTypes.object.isRequired,
}
