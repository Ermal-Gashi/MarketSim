import { useState } from 'react'
import PropTypes from 'prop-types'
import PersonaCards from './PersonaCards'
import HeroMap from './HeroMap'
import ObstacleCards from './ObstacleCards'
import MarketStats from './MarketStats'
import RadarChart from './RadarChart'
import CulturalFit from './CulturalFit'
import EntryRoadmap from './EntryRoadmap'
import BottomStrip from './BottomStrip'

// ── placeholder cell ──────────────────────────────────────────────────────────

function PlaceholderCell({ label, theme, style = {} }) {
  return (
    <div
      style={{
        background: theme.bgCard,
        border: `1px solid ${theme.borderDefault}`,
        borderRadius: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 12,
        color: theme.textMuted,
        ...style,
      }}
    >
      {label}
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function ReportDashboard({ completeReport, theme }) {
  // Fix 4 — shared archetype hover state, passed down to PersonaCards + HeroMap
  const [hoveredArchetype, setHoveredArchetype] = useState(null)

  const rowStyle = {
    borderTop: `1px solid ${theme.borderDefault}`,
    paddingTop: 24,
    width: '100%',
    boxSizing: 'border-box',
  }

  const threeColGrid = {
    display: 'grid',
    gridTemplateColumns: '1fr 2.5fr 1fr',
    gap: 16,
  }

  return (
    <div
      style={{
        paddingTop: 80,
        paddingLeft: 24,
        paddingRight: 24,
        paddingBottom: 48,
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
        overflowX: 'hidden',
        maxWidth: '100%',
        boxSizing: 'border-box',
      }}
    >
      {/* ── Row 1 — Hero: Personas | Map + Verdict | Obstacles ── */}
      <div style={rowStyle}>
        {/* Fix 3 — alignItems: stretch so all 3 columns match height */}
        <div style={{ ...threeColGrid, minHeight: 500, overflow: 'hidden', alignItems: 'stretch' }}>
          <PersonaCards
            personas={completeReport?.agent4_output?.personas || []}
            theme={theme}
            onArchetypeHover={setHoveredArchetype}
          />
          <HeroMap
            agent6Output={completeReport?.agent6_output || {}}
            agent7Output={completeReport?.agent7_output || {}}
            targetMarket={completeReport?.target_market}
            theme={theme}
            hoveredArchetype={hoveredArchetype}
          />
          <div style={{ minWidth: 0, overflow: 'hidden', height: '100%' }}>
            <ObstacleCards
              obstacles={completeReport?.agent5_output?.obstacles || []}
              theme={theme}
            />
          </div>
        </div>
      </div>

      {/* ── Row 2 — Analytics: Market Data | Signal Radar | Cultural Fit ── */}
      <div style={rowStyle}>
        <div style={{ ...threeColGrid, minHeight: 400, alignItems: 'stretch' }}>
          <div style={{ minWidth: 0 }}>
            <MarketStats agent2Output={completeReport?.agent2_output || {}} theme={theme} />
          </div>
          <div style={{ minWidth: 0 }}>
            <RadarChart radarScores={completeReport?.agent6_output?.radar_scores || {}} theme={theme} />
          </div>
          <div style={{ minWidth: 0 }}>
            <CulturalFit agent3Output={completeReport?.agent3_output || {}} theme={theme} />
          </div>
        </div>
      </div>

      {/* ── Row 3 — Entry Roadmap (full width) ── */}
      <div style={rowStyle}>
        <EntryRoadmap
          marketEntrySequence={completeReport?.agent6_output?.market_entry_sequence || []}
          theme={theme}
        />
      </div>

      {/* ── Row 4 — Bottom Strip ── */}
      <div style={rowStyle}>
        <BottomStrip
          agent6Output={completeReport?.agent6_output || {}}
          agent3Output={completeReport?.agent3_output || {}}
          agent2Output={completeReport?.agent2_output || {}}
          theme={theme}
        />
      </div>
    </div>
  )
}

ReportDashboard.propTypes = {
  completeReport: PropTypes.object,
  theme:          PropTypes.object.isRequired,
}
