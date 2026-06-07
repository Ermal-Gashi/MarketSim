import PropTypes from 'prop-types'

// ── helpers ───────────────────────────────────────────────────────────────────

function formatGdp(value) {
  if (value == null) return '—'
  return `$${Math.round(value).toLocaleString()}`
}

function formatPct(value) {
  if (value == null) return '—'
  return `${Number(value).toFixed(1)}%`
}

function formatPopulation(value) {
  if (value == null) return '—'
  const millions = value / 1_000_000
  return `${millions.toFixed(1)}M`
}

const MATURITY_STYLES = {
  Emerging:   { bg: 'rgba(201,168,76,0.15)',  text: '#C9A84C' },
  Developing: { bg: 'rgba(124,111,205,0.15)', text: '#7C6FCD' },
  Mature:     { bg: 'rgba(77,187,170,0.15)',  text: '#4DBBAA' },
}

const TREND_STYLES = {
  growing:     { label: '↑ Growing',     color: '#4DBBAA' },
  stable:      { label: '→ Stable',      color: null },     // resolved to theme.textSecondary at render
  contracting: { label: '↓ Contracting', color: '#C46B8A' },
}

// ── skeleton row ──────────────────────────────────────────────────────────────

function SkeletonRow({ theme, isLast }) {
  const pulse = {
    background: `linear-gradient(90deg, ${theme.borderDefault} 25%, ${theme.bgCard} 50%, ${theme.borderDefault} 75%)`,
    backgroundSize: '200% 100%',
    animation: 'skeleton-pulse 1.4s ease-in-out infinite',
    borderRadius: 4,
  }
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
      borderBottom: isLast ? 'none' : `1px solid ${theme.borderDefault}`,
    }}>
      <div style={{ ...pulse, width: '40%', height: 10, marginBottom: 8 }} />
      <div style={{ ...pulse, width: '55%', height: 18 }} />
    </div>
  )
}

// ── stat row ──────────────────────────────────────────────────────────────────

function StatRow({ label, children, theme, isLast }) {
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
      borderBottom: isLast ? 'none' : `1px solid ${theme.borderDefault}`,
    }}>
      <p style={{
        fontSize: 10, color: theme.textSecondary, textTransform: 'uppercase',
        letterSpacing: '0.06em', margin: '0 0 4px',
      }}>
        {label}
      </p>
      {children}
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function MarketStats({ agent2Output, theme }) {
  const hasData = agent2Output && Object.keys(agent2Output).length > 0

  const valueStyle = { fontSize: 18, fontWeight: 500, color: theme.textPrimary, margin: 0 }

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
        MARKET SNAPSHOT
      </p>

      {!hasData ? (
        <>
          {Array.from({ length: 5 }, (_, i) => (
            <SkeletonRow key={i} theme={theme} isLast={i === 4} />
          ))}
        </>
      ) : (
        <>
          <StatRow label="GDP per capita" theme={theme}>
            <p style={valueStyle}>{formatGdp(agent2Output.gdp_per_capita_usd)}</p>
          </StatRow>

          <StatRow label="Internet penetration" theme={theme}>
            <p style={valueStyle}>{formatPct(agent2Output.internet_penetration_pct)}</p>
          </StatRow>

          <StatRow label="Population" theme={theme}>
            <p style={valueStyle}>{formatPopulation(agent2Output.population)}</p>
          </StatRow>

          <StatRow label="Market maturity" theme={theme}>
            {agent2Output.market_maturity ? (
              (() => {
                const m = MATURITY_STYLES[agent2Output.market_maturity] ?? MATURITY_STYLES.Developing
                return (
                  <span style={{
                    display: 'inline-block', padding: '3px 10px', borderRadius: 12,
                    fontSize: 12, background: m.bg, color: m.text, width: 'fit-content',
                  }}>
                    {agent2Output.market_maturity}
                  </span>
                )
              })()
            ) : <p style={valueStyle}>—</p>}
          </StatRow>

          <StatRow label="Market trend" theme={theme} isLast>
            {agent2Output.market_trend ? (
              (() => {
                const t = TREND_STYLES[agent2Output.market_trend] ?? TREND_STYLES.stable
                return (
                  <p style={{ ...valueStyle, color: t.color ?? theme.textSecondary }}>
                    {t.label}
                  </p>
                )
              })()
            ) : <p style={valueStyle}>—</p>}
          </StatRow>
        </>
      )}
    </div>
  )
}

MarketStats.propTypes = {
  agent2Output: PropTypes.object,
  theme:        PropTypes.object.isRequired,
}
