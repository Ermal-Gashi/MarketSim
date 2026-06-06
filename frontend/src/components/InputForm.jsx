import { useState } from 'react'
import PropTypes from 'prop-types'

const labelClass = 'block text-xs font-normal mb-1.5 uppercase tracking-widest'
const labelStyle = { color: '#6B6B78' }

const inputStyle = {
  width: '100%',
  background: '#0D0D10',
  border: '1px solid #1C1C22',
  borderRadius: 8,
  padding: '0.75rem',
  color: '#D0D0D8',
  fontSize: 14,
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.15s',
  resize: 'none',
}

const TIPS = [
  {
    label: 'Your product',
    text: 'describe what it does, who buys it, and roughly what it costs. More detail produces sharper personas and more accurate cultural analysis.',
  },
  {
    label: 'Current market',
    text: 'where you operate today, e.g. United States or Western Europe.',
  },
  {
    label: 'Target market',
    text: 'the country or region you want to enter, e.g. Brazil or Japan. Single countries work best.',
  },
]

function Field({ label, children }) {
  return (
    <div className="mb-4">
      <label className={labelClass} style={labelStyle}>{label}</label>
      {children}
    </div>
  )
}

function StyledInput({ as: Tag = 'input', ...props }) {
  const [focused, setFocused] = useState(false)
  return (
    <Tag
      style={{ ...inputStyle, borderColor: focused ? '#2E2E3A' : '#1C1C22' }}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      {...props}
    />
  )
}

export default function InputForm({ startSimulation, isRunning, onSimulationStart }) {
  const [productDescription, setProductDescription] = useState('')
  const [currentMarket, setCurrentMarket] = useState('')
  const [targetMarket, setTargetMarket] = useState('')
  const [validationError, setValidationError] = useState('')
  const [tipsOpen, setTipsOpen] = useState(false)

  const allFilled =
    productDescription.trim().length > 0 &&
    currentMarket.trim().length > 0 &&
    targetMarket.trim().length > 0

  const handleSubmit = (e) => {
    e.preventDefault()
    const pd = productDescription.trim()
    const cm = currentMarket.trim()
    const tm = targetMarket.trim()

    if (!pd || !cm || !tm) {
      setValidationError('Please fill in all fields')
      return
    }

    setValidationError('')
    startSimulation(pd, cm, tm)
    onSimulationStart()
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div style={{ width: '100%', maxWidth: 520 }}>
        <div
          style={{
            background: '#111116',
            borderTop: '1px solid #2E2E3A',
            borderRight: '1px solid #1C1C22',
            borderBottom: '1px solid #1C1C22',
            borderLeft: '1px solid #1C1C22',
            borderRadius: 16,
            padding: '2.5rem',
          }}
        >
          {/* Wordmark */}
          <p
            style={{
              fontSize: 13,
              fontWeight: 400,
              letterSpacing: '0.18em',
              color: '#6B6B78',
              textTransform: 'uppercase',
              marginBottom: '1.5rem',
            }}
          >
            MarketSim
          </p>

          {/* Headline */}
          <h1
            style={{
              fontSize: 26,
              fontWeight: 600,
              color: '#E8E8ED',
              lineHeight: 1.2,
              margin: 0,
            }}
          >
            Simulate your market entry
          </h1>

          {/* Subheadline */}
          <p
            style={{
              fontSize: 14,
              color: '#6B6B78',
              marginTop: '0.5rem',
              marginBottom: '1rem',
            }}
          >
            Real data. Seven agents. One verdict.
          </p>

          {/* Collapsible tips */}
          <div style={{ marginBottom: '1.5rem' }}>
            <button
              type="button"
              onClick={() => setTipsOpen((o) => !o)}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                cursor: 'pointer',
                color: '#6B6B78',
                fontSize: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <span style={{ fontSize: 10 }}>{tipsOpen ? '▾' : '▸'}</span>
              How to get the best results
            </button>

            <div
              style={{
                overflow: 'hidden',
                maxHeight: tipsOpen ? 200 : 0,
                transition: 'max-height 0.3s ease',
              }}
            >
              <ul
                style={{
                  marginTop: '0.75rem',
                  paddingLeft: 12,
                  borderLeft: '2px solid #1C1C22',
                  listStyle: 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                }}
              >
                {TIPS.map((tip) => (
                  <li key={tip.label} style={{ fontSize: 12, lineHeight: 1.6, color: '#6B6B78' }}>
                    <span style={{ color: '#8B3A52', marginRight: 6 }}>—</span>
                    <strong style={{ color: '#6B6B78', fontWeight: 500 }}>{tip.label}</strong>
                    {' — '}
                    {tip.text}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {/* Product description */}
            <Field label="Your product">
              <StyledInput
                as="textarea"
                rows={4}
                placeholder="Describe your product in 1-3 sentences — what it does, who it serves, how it works"
                value={productDescription}
                onChange={(e) => setProductDescription(e.target.value)}
                disabled={isRunning}
              />
              {/* Character counter */}
              <p
                style={{
                  fontSize: 11,
                  color: productDescription.length > 500 ? '#8B3A52' : '#6B6B78',
                  textAlign: 'right',
                  marginTop: 4,
                }}
              >
                {productDescription.length} / 500 characters
              </p>
            </Field>

            <div className="grid grid-cols-2 gap-3 mb-0">
              <Field label="Current market">
                <StyledInput
                  type="text"
                  placeholder="e.g. United States"
                  value={currentMarket}
                  onChange={(e) => setCurrentMarket(e.target.value)}
                  disabled={isRunning}
                />
              </Field>
              <Field label="Target market">
                <StyledInput
                  type="text"
                  placeholder="e.g. Brazil"
                  value={targetMarket}
                  onChange={(e) => setTargetMarket(e.target.value)}
                  disabled={isRunning}
                />
              </Field>
            </div>

            {validationError && (
              <p style={{ color: '#8B3A52', fontSize: 12, marginTop: '0.75rem' }}>
                {validationError}
              </p>
            )}

            <button
              type="submit"
              disabled={isRunning}
              className={`btn-run${allFilled && !isRunning ? ' btn-run-ready' : ''}`}
              style={{
                width: '100%',
                height: 48,
                fontWeight: 400,
                fontSize: 15,
                marginTop: '1.5rem',
                letterSpacing: '0.02em',
              }}
            >
              {isRunning ? 'Running simulation…' : 'Run Simulation'}
              <span className="btn-corners" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

InputForm.propTypes = {
  startSimulation: PropTypes.func.isRequired,
  isRunning: PropTypes.bool.isRequired,
  onSimulationStart: PropTypes.func.isRequired,
}
