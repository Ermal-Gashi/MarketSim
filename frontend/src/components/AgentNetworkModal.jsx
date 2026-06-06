import { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'

// ── constants ────────────────────────────────────────────────────────────────

const PURPLE = '#8B6FCD'
const WINE   = '#8B3A52'

// AGENT_COLORS is built at draw time using theme.accentActive for agents 0-4
function buildAgentColors(accentActive) {
  return [accentActive, accentActive, accentActive, accentActive, accentActive, PURPLE, WINE]
}

const CX = 330
const CY = 210
const ORBIT_R = 155
const NODE_R  = 20

function nodePos(i) {
  const angle = (i / 7) * Math.PI * 2 - Math.PI / 2
  return {
    x: CX + ORBIT_R * Math.cos(angle),
    y: CY + ORBIT_R * Math.sin(angle),
  }
}

const POSITIONS = Array.from({ length: 7 }, (_, i) => nodePos(i))

// ── canvas renderer ──────────────────────────────────────────────────────────

function drawNetwork(canvas, agentStatuses, tick, particles, theme, accentActive) {
  const AGENT_COLORS = buildAgentColors(accentActive)
  const ctx = canvas.getContext('2d')

  // disable anti-alias blur on lines
  ctx.imageSmoothingEnabled = false

  // fill canvas background to match modal card exactly
  ctx.fillStyle = theme.bgCard
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const statuses = agentStatuses.map((a) => a.status)

  // ── connection lines ──
  // pre-parse borderDefault hex once for rgba usage
  const bdHex = theme.borderDefault.replace('#', '')
  const bdR   = parseInt(bdHex.slice(0, 2), 16)
  const bdG   = parseInt(bdHex.slice(2, 4), 16)
  const bdB   = parseInt(bdHex.slice(4, 6), 16)

  for (let i = 0; i < 7; i++) {
    for (let j = i + 1; j < 7; j++) {
      const bothDone = statuses[i] === 'done' && statuses[j] === 'done'
      ctx.beginPath()
      ctx.moveTo(POSITIONS[i].x, POSITIONS[i].y)
      ctx.lineTo(POSITIONS[j].x, POSITIONS[j].y)
      if (bothDone) {
        ctx.strokeStyle = 'rgba(77,187,170,0.3)'
        ctx.lineWidth   = 1
      } else {
        ctx.strokeStyle = `rgba(${bdR},${bdG},${bdB},0.5)`
        ctx.lineWidth   = 0.5
      }
      ctx.stroke()
    }
  }

  // ── center label ──
  ctx.font         = '500 10px system-ui, sans-serif'
  ctx.fillStyle    = theme.textMuted
  ctx.textAlign    = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('MarketSim', CX, CY)

  // ── particles ──
  for (const p of particles) {
    const x     = POSITIONS[p.src].x + (POSITIONS[p.dst].x - POSITIONS[p.src].x) * p.t
    const y     = POSITIONS[p.src].y + (POSITIONS[p.dst].y - POSITIONS[p.src].y) * p.t
    const alpha = Math.sin(p.t * Math.PI)   // fade in/out, peak at t=0.5
    ctx.beginPath()
    ctx.arc(x, y, 2.5, 0, Math.PI * 2)
    ctx.fillStyle    = AGENT_COLORS[p.src]
    ctx.globalAlpha  = alpha
    ctx.fill()
    ctx.globalAlpha  = 1
  }

  // ── nodes ──
  for (let i = 0; i < 7; i++) {
    const { x, y } = POSITIONS[i]
    const status    = statuses[i]
    const color     = AGENT_COLORS[i]

    // glow for running node
    if (status === 'running') {
      const glow = 0.5 + 0.5 * Math.sin(tick * 0.08)
      ctx.shadowColor = accentActive
      ctx.shadowBlur  = 12 * glow
    } else {
      ctx.shadowBlur = 0
    }

    // node fill + stroke
    ctx.beginPath()
    ctx.arc(x, y, NODE_R, 0, Math.PI * 2)

    if (status === 'waiting') {
      ctx.fillStyle   = theme.bgCard
      ctx.strokeStyle = theme.borderStrong
      ctx.lineWidth   = 1
    } else if (status === 'running') {
      const hex = accentActive.replace('#', '')
      const rr  = parseInt(hex.slice(0, 2), 16)
      const gg  = parseInt(hex.slice(2, 4), 16)
      const bb  = parseInt(hex.slice(4, 6), 16)
      ctx.fillStyle   = `rgba(${rr},${gg},${bb},0.15)`
      ctx.strokeStyle = accentActive
      ctx.lineWidth   = 1.5
    } else {
      // done — accent colour at 20% opacity fill
      const hex = color.replace('#', '')
      const r   = parseInt(hex.slice(0, 2), 16)
      const g   = parseInt(hex.slice(2, 4), 16)
      const b   = parseInt(hex.slice(4, 6), 16)
      ctx.fillStyle   = `rgba(${r},${g},${b},0.2)`
      ctx.strokeStyle = color
      ctx.lineWidth   = 1.5
    }

    ctx.fill()
    ctx.stroke()
    ctx.shadowBlur = 0

    // ── node label (A1–A7) ──
    const labelColor =
      status === 'waiting' ? theme.textMuted
      : status === 'running' ? accentActive
      : color
    ctx.font         = '500 9px system-ui, sans-serif'
    ctx.fillStyle    = labelColor
    ctx.textAlign    = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(`A${i + 1}`, x, y)

    // ── agent name above / below node ──
    const above     = y < CY
    const nameY     = above ? y - (NODE_R + 13) : y + (NODE_R + 13)
    const nameColor =
      status === 'waiting' ? theme.borderStrong : theme.textSecondary

    ctx.font         = '9px system-ui, sans-serif'
    ctx.fillStyle    = nameColor
    ctx.textAlign    = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(agentStatuses[i].name, x, nameY)
  }
}

// ── component ────────────────────────────────────────────────────────────────

export default function AgentNetworkModal({ isOpen, onClose, agentStatuses, theme }) {
  const canvasRef     = useRef(null)
  const rafRef        = useRef(null)
  const tickRef       = useRef(0)
  const particleRef   = useRef([])
  const spawnCountRef = useRef(0)

  useEffect(() => {
    if (!isOpen) {
      cancelAnimationFrame(rafRef.current)
      particleRef.current = []
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    function loop() {
      tickRef.current      += 1
      spawnCountRef.current += 1

      const doneIndices = agentStatuses
        .map((a, i) => ({ status: a.status, i }))
        .filter((a) => a.status === 'done')
        .map((a) => a.i)

      // spawn particle every 20 frames if 2+ agents done
      if (spawnCountRef.current % 20 === 0 && doneIndices.length >= 2) {
        const shuffled = [...doneIndices].sort(() => Math.random() - 0.5)
        particleRef.current.push({ src: shuffled[0], dst: shuffled[1], t: 0 })
      }

      // advance + prune particles
      particleRef.current = particleRef.current
        .map((p) => ({ ...p, t: p.t + 0.018 }))
        .filter((p) => p.t < 1)

      drawNetwork(canvas, agentStatuses, tickRef.current, particleRef.current, theme, theme.accentActive)
      rafRef.current = requestAnimationFrame(loop)
    }

    rafRef.current = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(rafRef.current)
  }, [isOpen, agentStatuses, theme])

  if (!isOpen) return null

  return (
    /* overlay — always dark */
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.55)',
        backdropFilter: 'blur(6px)',
        WebkitBackdropFilter: 'blur(6px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* modal box */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 720,
          maxWidth: '92vw',
          background: theme.bgCard,
          border: `1px solid ${theme.borderDefault}`,
          borderRadius: 16,
          overflow: 'hidden',
        }}
      >
        {/* header */}
        <div
          style={{
            padding: '1rem 1.25rem',
            borderBottom: `1px solid ${theme.borderDefault}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <span style={{ fontSize: 13, color: theme.textSecondary, fontWeight: 500 }}>
              Agent neural network
            </span>
            <span style={{ display: 'block', fontSize: 11, color: theme.textMuted, marginTop: 2 }}>
              7 agents · real-time data flow
            </span>
          </div>

          <button
            onClick={onClose}
            style={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              background: theme.borderDefault,
              border: 'none',
              cursor: 'pointer',
              color: theme.textSecondary,
              fontSize: 14,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>

        {/* canvas */}
        <div style={{ padding: '1rem 1.25rem', display: 'flex', justifyContent: 'center' }}>
          <canvas ref={canvasRef} id="networkCanvas" width={660} height={420} />
        </div>

        {/* legend */}
        <div
          style={{
            padding: '0.75rem 1.25rem',
            borderTop: `1px solid ${theme.borderDefault}`,
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
          }}
        >
          {[
            { label: 'Complete',  color: theme.accentActive,  pulse: false },
            { label: 'Running',   color: theme.accentActive,  pulse: true  },
            { label: 'Waiting',   color: theme.borderDefault, pulse: false },
            { label: 'Sim Layer', color: WINE,                pulse: false },
          ].map(({ label, color, pulse }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: color,
                  display: 'inline-block',
                  animation: pulse ? 'pill-pulse 1.4s ease-in-out infinite' : 'none',
                  flexShrink: 0,
                }}
              />
              <span style={{ fontSize: 11, color: theme.textMuted }}>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

AgentNetworkModal.propTypes = {
  isOpen:        PropTypes.bool.isRequired,
  onClose:       PropTypes.func.isRequired,
  agentStatuses: PropTypes.arrayOf(
    PropTypes.shape({
      agentNumber: PropTypes.number.isRequired,
      name:        PropTypes.string.isRequired,
      status:      PropTypes.oneOf(['waiting', 'running', 'done', 'error']).isRequired,
    })
  ).isRequired,
  theme: PropTypes.object.isRequired,
}
