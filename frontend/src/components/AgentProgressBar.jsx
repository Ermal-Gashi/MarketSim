import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PropTypes from 'prop-types'
import { themes } from '../theme'

// ── constants ────────────────────────────────────────────────────────────────

// TEAL kept only for ThinkingDots — pills use theme.accentActive
const TEAL = '#4DBBAA'

const EVOCATIVE = {
  1: 'Decoding your product DNA',
  2: 'Pulling live market intelligence',
  3: 'Reading the cultural landscape',
  4: 'Building your buyer archetypes',
  5: 'Stress testing the entry path',
  6: 'Weighing all the signals',
  7: 'Simulating 200 potential customers',
}

const SUBTITLE = {
  1: 'Extracting value props, pricing tier, and customer profile',
  2: 'Fetching World Bank data, competitors, and market infrastructure',
  3: 'Scoring cultural fit against Hofstede dimensions for this market',
  4: 'Generating 5 synthetic buyer archetypes with variance profiles',
  5: 'Surfacing the top obstacles grounded in real governance data',
  6: 'Producing the final verdict, regional weights, and entry roadmap',
  7: 'Rolling 200 synthetic customer instances across the target market',
}

// ── sub-components ───────────────────────────────────────────────────────────

// Change 1 — dots increased from 4px to 8px diameter
function ThinkingDots() {
  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            display: 'inline-block',
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: TEAL,
            animation: `dot-pulse 1.2s ease-in-out ${i * 0.4}s infinite`,
          }}
        />
      ))}
    </div>
  )
}

function Pill({ status, theme }) {
  const isRunning = status === 'running'
  const isDone    = status === 'done'
  return (
    <div
      style={{
        width: 28,
        height: 5,
        borderRadius: 3,
        flexShrink: 0,
        background: isDone || isRunning ? theme.accentActive : theme.borderDefault,
        animation: isRunning ? 'pill-pulse 1.4s ease-in-out infinite' : 'none',
      }}
    />
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function AgentProgressBar({ agentStatuses, currentAgent, isComplete, theme, onViewNetwork, onCancel }) {
  const [viewHovered, setViewHovered] = useState(false)
  const [cancelHovered, setCancelHovered] = useState(false)

  return (
    <>
      {/* ── Fixed top bar ───────────────────────────────────────── */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 40,
          height: 52,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1.5rem',
          background: theme.bgBar,
          borderBottom: `1px solid ${theme.borderDefault}`,
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
        }}
      >
        {/* Left — wordmark + View network when complete */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 160 }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 500,
              letterSpacing: '0.12em',
              color: theme.textMuted,
              textTransform: 'uppercase',
              whiteSpace: 'nowrap',
            }}
          >
            MarketSim
          </span>
          {isComplete && (
            <>
              <span style={{ color: theme.borderStrong, fontSize: 12 }}>|</span>
              <button
                onClick={onViewNetwork}
                onMouseEnter={() => setViewHovered(true)}
                onMouseLeave={() => setViewHovered(false)}
                style={{
                  fontSize: 11,
                  color: theme.accentActive,
                  border: `1px solid ${theme.accentActive}`,
                  borderRadius: 6,
                  padding: '4px 10px',
                  background: 'transparent',
                  cursor: 'pointer',
                  transition: 'opacity 0.15s',
                  opacity: viewHovered ? 0.7 : 1,
                  whiteSpace: 'nowrap',
                }}
              >
                View network
              </button>
            </>
          )}
        </div>

        {/* Center — 7 pills */}
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          {agentStatuses.map((agent) => (
            <Pill key={agent.agentNumber} status={agent.status} theme={theme} />
          ))}
        </div>

        {/* Right — spacer to balance left side and keep pills centered */}
        <div style={{ minWidth: 160 }} />
      </div>

      {/* ── Center status area — hidden when complete (ReportDashboard takes over) ── */}
      {!isComplete && (
      <div
        style={{
          minHeight: 'calc(100vh - 52px)',
          marginTop: 52,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-start',
          paddingTop: 'calc(15vh)',
        }}
      >
        <AnimatePresence mode="wait">
          {isComplete ? (
            /* Change 4 — "Simulation complete" fades in after running text fades out */
            <motion.div
              key="complete"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}
            >
              {/* Change 1 — "Simulation complete" at 42px */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ color: theme.accentActive, fontSize: 38 }}>✓</span>
                <span style={{ fontSize: 42, fontWeight: 600, color: theme.textPrimary }}>
                  Simulation complete
                </span>
              </div>

              {/* Change 5 — Cancel button always below status text */}
              <div style={{ marginTop: '1.5rem' }}>
                <button
                  onClick={onCancel}
                  onMouseEnter={() => setCancelHovered(true)}
                  onMouseLeave={() => setCancelHovered(false)}
                  style={{
                    fontSize: 12,
                    color: cancelHovered ? theme.accentWine : theme.textSecondary,
                    border: `1px solid ${cancelHovered ? theme.accentWine : theme.borderStrong}`,
                    borderRadius: 6,
                    padding: '6px 16px',
                    background: 'transparent',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s, color 0.15s',
                  }}
                >
                  Cancel
                </button>
              </div>
            </motion.div>
          ) : currentAgent !== null ? (
            /* Change 4 — running text fades out (0.8s) when isComplete becomes true */
            <motion.div
              key={currentAgent}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}
            >
              {/* Change 1 — evocative name: 52px, weight 600 */}
              <p style={{ fontSize: 52, fontWeight: 600, color: theme.textPrimary, marginBottom: 12 }}>
                {EVOCATIVE[currentAgent]}
              </p>
              {/* Change 1 — subtitle: 18px */}
              <p style={{ fontSize: 18, color: theme.textSecondary, marginBottom: 28 }}>
                {SUBTITLE[currentAgent]}
              </p>
              <ThinkingDots />

              {/* Change 3 — "View network" stays below during running */}
              {/* Change 5 — Cancel stays below in all running states */}
              <div style={{ display: 'flex', gap: 10, marginTop: '1.5rem' }}>
                <button
                  onClick={onViewNetwork}
                  onMouseEnter={() => setViewHovered(true)}
                  onMouseLeave={() => setViewHovered(false)}
                  style={{
                    fontSize: 12,
                    color: theme.accentActive,
                    border: `1px solid ${theme.accentActive}`,
                    borderRadius: 6,
                    padding: '6px 16px',
                    background: 'transparent',
                    cursor: 'pointer',
                    transition: 'opacity 0.15s',
                    opacity: viewHovered ? 0.75 : 1,
                  }}
                >
                  View network
                </button>
                <button
                  onClick={onCancel}
                  onMouseEnter={() => setCancelHovered(true)}
                  onMouseLeave={() => setCancelHovered(false)}
                  style={{
                    fontSize: 12,
                    color: cancelHovered ? theme.accentWine : theme.textSecondary,
                    border: `1px solid ${cancelHovered ? theme.accentWine : theme.borderStrong}`,
                    borderRadius: 6,
                    padding: '6px 16px',
                    background: 'transparent',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s, color 0.15s',
                  }}
                >
                  Cancel
                </button>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
      )}
    </>
  )
}

AgentProgressBar.propTypes = {
  agentStatuses: PropTypes.arrayOf(
    PropTypes.shape({
      agentNumber: PropTypes.number.isRequired,
      name:        PropTypes.string.isRequired,
      status:      PropTypes.oneOf(['waiting', 'running', 'done', 'error']).isRequired,
    })
  ).isRequired,
  currentAgent:  PropTypes.number,
  isComplete:    PropTypes.bool.isRequired,
  theme:         PropTypes.object.isRequired,
  onViewNetwork: PropTypes.func.isRequired,
  onCancel:      PropTypes.func.isRequired,
}

// ── Demo export for visual testing ────────────────────────────────────────────

const DEMO_STATUSES = [
  { agentNumber: 1, name: 'Product Analyst',      status: 'done' },
  { agentNumber: 2, name: 'Market Data Fetcher',  status: 'done' },
  { agentNumber: 3, name: 'Cultural Fit Scorer',  status: 'running' },
  { agentNumber: 4, name: 'Persona Generator',    status: 'waiting' },
  { agentNumber: 5, name: 'Obstacle Detector',    status: 'waiting' },
  { agentNumber: 6, name: 'Synthesizer',          status: 'waiting' },
  { agentNumber: 7, name: 'Simulation Layer',     status: 'waiting' },
]

export function AgentProgressBarDemo() {
  return (
    <AgentProgressBar
      agentStatuses={DEMO_STATUSES}
      currentAgent={3}
      isComplete={false}
      theme={themes.dark}
      onViewNetwork={() => console.log('view network clicked')}
      onCancel={() => console.log('cancel clicked')}
    />
  )
}
