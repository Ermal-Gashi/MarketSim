import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import useSimulation from './hooks/useSimulation'
import { themes } from './theme'
import InputForm from './components/InputForm'
import AgentProgressBar from './components/AgentProgressBar'
import AgentNetworkModal from './components/AgentNetworkModal'
import ReportDashboard from './components/ReportDashboard'
// import HeroMap from './components/HeroMap'
// import RadarChart from './components/RadarChart'
// import PersonaCards from './components/PersonaCards'
// import ObstacleMatrix from './components/ObstacleMatrix'
// import EntryRoadmap from './components/EntryRoadmap'
// import VerdictSummary from './components/VerdictSummary'

function gridBackground(theme) {
  return {
    backgroundColor: theme.bgPage,
    backgroundImage: `
      linear-gradient(${theme.gridMajor} 1px, transparent 1px),
      linear-gradient(90deg, ${theme.gridMajor} 1px, transparent 1px),
      linear-gradient(${theme.gridMinor} 1px, transparent 1px),
      linear-gradient(90deg, ${theme.gridMinor} 1px, transparent 1px)
    `,
    backgroundSize: '150px 150px, 150px 150px, 30px 30px, 30px 30px',
    backgroundPosition: '-1px -1px, -1px -1px, -1px -1px, -1px -1px',
  }
}

// TEMP: set to false before production
const TEST_MODE = true

const MOCK_REPORT = {
  product_description: 'Test chip brand',
  current_market: 'United States',
  target_market: 'Germany',
  agent1_output: {},
  agent2_output: {
    country_name: 'Germany',
    gdp_per_capita_usd: 48400,
    internet_penetration_pct: 91,
    population: 83200000,
    market_maturity: 'Mature',
    market_trend: 'Stable',
    major_local_competitors: ['Aldi', 'Lidl', 'Rewe'],
  },
  agent3_output: {
    fit_score: 62,
    score_label: 'Moderate Fit',
    dimension_analysis: [
      { dimension: 'Power Distance', score: 35 },
      { dimension: 'Individualism', score: 67 },
      { dimension: 'Masculinity', score: 66 },
      { dimension: 'Uncertainty Avoidance', score: 65 },
      { dimension: 'Long Term Orientation', score: 83 },
      { dimension: 'Indulgence', score: 40 },
    ],
  },
  agent4_output: {
    personas: [
      {
        name: 'Markus', age: 38,
        job_title: 'Operations Manager',
        city: 'Munich',
        purchase_likelihood: 'High',
        archetype_label: 'The Pragmatist',
        why_they_buy: 'Efficiency and cost reduction',
        what_stops_them: 'Switching costs from existing supplier',
        how_they_discover: 'Industry trade shows and LinkedIn',
        variance_profile: { conversion_range: '65–80%', tipping_point_to_high: 'Free trial', tipping_point_to_low: 'Poor support SLA' },
      },
      {
        name: 'Anna', age: 29,
        job_title: 'Product Designer',
        city: 'Berlin',
        purchase_likelihood: 'Medium',
        archetype_label: 'The Innovator',
        why_they_buy: 'Novel form factor and sustainability angle',
        what_stops_them: 'Price premium vs local alternatives',
        how_they_discover: 'Design blogs and Instagram',
        variance_profile: { conversion_range: '40–60%', tipping_point_to_high: 'Co-branding opportunity', tipping_point_to_low: 'No EU-made claim' },
      },
      {
        name: 'Stefan', age: 52,
        job_title: 'Procurement Director',
        city: 'Hamburg',
        purchase_likelihood: 'Low',
        archetype_label: 'The Gatekeeper',
        why_they_buy: 'Only if mandated by regulation',
        what_stops_them: 'Risk aversion, incumbent relationships',
        how_they_discover: 'Vendor whitepapers and analyst reports',
        variance_profile: { conversion_range: '10–25%', tipping_point_to_high: 'Pilot with measurable ROI', tipping_point_to_low: 'Any compliance risk' },
      },
      {
        name: 'Julia', age: 34,
        job_title: 'E-commerce Manager',
        city: 'Frankfurt',
        purchase_likelihood: 'High',
        archetype_label: 'The Growth Hacker',
        why_they_buy: 'Margins and consumer trend alignment',
        what_stops_them: 'Uncertain brand recognition in DE market',
        how_they_discover: 'DTC newsletters and Shopify ecosystem',
        variance_profile: { conversion_range: '60–75%', tipping_point_to_high: 'Influencer validation', tipping_point_to_low: 'Poor delivery SLA' },
      },
      {
        name: 'Klaus', age: 45,
        job_title: 'Category Buyer',
        city: 'Cologne',
        purchase_likelihood: 'Medium',
        archetype_label: 'The Analyst',
        why_they_buy: 'Data-driven shelf performance metrics',
        what_stops_them: 'Needs 2+ quarters of EU sales data',
        how_they_discover: 'Nielsen reports and category reviews',
        variance_profile: { conversion_range: '35–55%', tipping_point_to_high: 'Retail pilot results', tipping_point_to_low: 'Weak velocity data' },
      },
    ],
  },
  agent5_output: {
    obstacles: [
      {
        title: 'EU Food Labelling Compliance',
        severity: 'Critical',
        category: 'Regulatory',
        description: 'DE requires all packaging in German with full nutritional breakdown under EU 1169/2011.',
        mitigation: 'Engage a local compliance consultancy before launch. Budget €15k–€30k for packaging redesign.',
        time_sensitivity: 'Must resolve before any retail listing',
        cost_to_fix: '€15,000–€30,000',
        early_warning_signal: 'Retailer requests allergen declaration form',
      },
      {
        title: 'Retail Slotting Fee Culture',
        severity: 'High',
        category: 'Market Access',
        description: 'Major German grocery chains charge significant slotting fees and require promotional commitments.',
        mitigation: 'Start with online DTC and specialty retailers to build velocity data before approaching Rewe or Edeka.',
        time_sensitivity: '6–12 months before retail approach',
        cost_to_fix: '€50,000–€150,000 in slotting and promos',
        early_warning_signal: 'Buyer asks for previous EU velocity reports',
      },
      {
        title: 'High Private Label Competition',
        severity: 'High',
        category: 'Competitive',
        description: 'Aldi and Lidl private label products undercut branded goods by 30–40% on price.',
        mitigation: 'Compete on premiumization, sustainability credentials, and origin story rather than price.',
        time_sensitivity: 'Ongoing',
        cost_to_fix: 'Marketing investment €80k+ Year 1',
        early_warning_signal: 'Price comparison sites rank product above 3rd quartile',
      },
      {
        title: 'VAT Registration & Local Entity',
        severity: 'Medium',
        category: 'Legal',
        description: 'Selling B2B or via marketplace in Germany typically triggers VAT registration requirements.',
        mitigation: 'Engage a German tax advisor and register for DE VAT (19%) before first commercial transaction.',
        time_sensitivity: '3 months lead time',
        cost_to_fix: '€3,000–€8,000 advisor fees',
        early_warning_signal: 'First marketplace sale or B2B invoice raised',
      },
      {
        title: 'Consumer Trust & Brand Awareness',
        severity: 'Low',
        category: 'Brand',
        description: 'German consumers are skeptical of unknown foreign brands and rely heavily on peer reviews.',
        mitigation: 'Invest in German-language content, local influencers, and Trusted Shops certification.',
        time_sensitivity: '12–18 month brand-building window',
        cost_to_fix: '€20,000–€60,000 in brand marketing',
        early_warning_signal: 'Review velocity below 10 per month after 90 days',
      },
    ],
  },
  agent6_output: {
    verdict: 'Cautious Go',
    verdict_reason: 'Strong digital channel opportunity tempered by regulatory complexity and entrenched private label competition.',
    confidence_score: 64,
    executive_summary: 'Germany presents a viable but demanding market entry for a premium chip brand. Digital-first approach recommended.',
    regional_weights: { Bavaria: 0.28, 'North Rhine-Westphalia': 0.24, Baden: 0.18, Hamburg: 0.14, Berlin: 0.16 },
    radar_scores: { 'Market Growth': 62, 'Cultural Fit': 58, 'Internet Penetration': 88, 'Political Stability': 85, 'Ease of Business': 72, 'Corruption Index': 80 },
    market_entry_sequence: [
      { phase_name: 'Compliance & Setup', timeframe: 'Month 1–3', actions: ['VAT registration', 'Packaging redesign', 'Legal entity setup'] },
      { phase_name: 'DTC Pilot', timeframe: 'Month 3–6', actions: ['Amazon.de + own webshop', 'German SEO content', 'Micro-influencer seeding'] },
      { phase_name: 'Specialty Retail', timeframe: 'Month 6–12', actions: ['Approach deli chains', 'Bio/organic retailers', 'Build velocity data'] },
      { phase_name: 'Scale', timeframe: 'Month 12–24', actions: ['Approach Rewe/Edeka', 'Regional TV campaign', 'Private label defence strategy'] },
    ],
    critical_assumptions: [
      'Premium positioning holds vs private label at €2.50+ price point',
      'EU customs costs remain stable post-Brexit supply chain reroute',
      'Target €1M GMV within 18 months to justify retail expansion',
    ],
    recommended_first_move: 'Launch on Amazon.de with German-language listing optimised for "American Chips" search terms, targeting €15k GMV in Month 1.',
    biggest_wildcard: 'A major German food retailer launching their own American-style premium chip line within 12 months of entry.',
  },
  agent7_output: {
    instances: [
      { archetype: 'The Pragmatist', city: 'Munich', lat: 48.1351, lng: 11.5820, conversion_outcome: 'converted', confidence_score: 78, pulse_intensity: 0.9, spawn_delay_ms: 200, display_name: 'Markus B.', job_title: 'Operations Manager', avatar_style: 'initials', outcome_reason: 'ROI clear within quarter', deciding_factor: 'Free trial offer' },
      { archetype: 'The Innovator', city: 'Berlin', lat: 52.5200, lng: 13.4050, conversion_outcome: 'evaluating', confidence_score: 52, pulse_intensity: 0.6, spawn_delay_ms: 600, display_name: 'Anna K.', job_title: 'Product Designer', avatar_style: 'initials', outcome_reason: 'Comparing with local brand', deciding_factor: 'Sustainability credentials' },
      { archetype: 'The Gatekeeper', city: 'Hamburg', lat: 53.5511, lng: 9.9937, conversion_outcome: 'abandoned', confidence_score: 18, pulse_intensity: 0.2, spawn_delay_ms: 1000, display_name: 'Stefan M.', job_title: 'Procurement Director', avatar_style: 'initials', outcome_reason: 'Compliance risk flagged', deciding_factor: 'Regulatory uncertainty' },
      { archetype: 'The Growth Hacker', city: 'Frankfurt', lat: 50.1109, lng: 8.6821, conversion_outcome: 'converted', confidence_score: 71, pulse_intensity: 0.85, spawn_delay_ms: 400, display_name: 'Julia R.', job_title: 'E-commerce Manager', avatar_style: 'initials', outcome_reason: 'Influencer validated', deciding_factor: 'Brand story resonance' },
      { archetype: 'The Analyst', city: 'Cologne', lat: 50.9333, lng: 6.9500, conversion_outcome: 'evaluating', confidence_score: 44, pulse_intensity: 0.5, spawn_delay_ms: 800, display_name: 'Klaus W.', job_title: 'Category Buyer', avatar_style: 'initials', outcome_reason: 'Awaiting velocity data', deciding_factor: 'Retail pilot results' },
      { archetype: 'The Pragmatist', city: 'Stuttgart', lat: 48.7758, lng: 9.1829, conversion_outcome: 'converted', confidence_score: 74, pulse_intensity: 0.88, spawn_delay_ms: 1200, display_name: 'Petra S.', job_title: 'Supply Chain Lead', avatar_style: 'initials', outcome_reason: 'Cost savings verified', deciding_factor: 'Free trial offer' },
      { archetype: 'The Innovator', city: 'Düsseldorf', lat: 51.2217, lng: 6.7762, conversion_outcome: 'abandoned', confidence_score: 22, pulse_intensity: 0.25, spawn_delay_ms: 1500, display_name: 'Tobias F.', job_title: 'Brand Strategist', avatar_style: 'initials', outcome_reason: 'No EU-made claim', deciding_factor: 'Origin transparency' },
    ],
    summary: {},
  },
}

const MOCK_AGENT_STATUSES = [
  { agentNumber: 1, name: 'Product Analyst',      status: 'done', output: {}, error: null },
  { agentNumber: 2, name: 'Market Data Fetcher',  status: 'done', output: {}, error: null },
  { agentNumber: 3, name: 'Cultural Fit Scorer',  status: 'done', output: {}, error: null },
  { agentNumber: 4, name: 'Persona Generator',    status: 'done', output: {}, error: null },
  { agentNumber: 5, name: 'Obstacle Detector',    status: 'done', output: {}, error: null },
  { agentNumber: 6, name: 'Synthesizer',          status: 'done', output: {}, error: null },
  { agentNumber: 7, name: 'Simulation Layer',     status: 'done', output: {}, error: null },
]

export default function App() {
  const {
    agentStatuses: liveAgentStatuses,
    isRunning,
    isComplete: liveIsComplete,
    completeReport: liveCompleteReport,
    error,
    currentAgent,
    startSimulation,
    reset,
  } = useSimulation()

  const agentStatuses  = TEST_MODE ? MOCK_AGENT_STATUSES : liveAgentStatuses
  const isComplete     = TEST_MODE ? true                : liveIsComplete
  const completeReport = TEST_MODE ? MOCK_REPORT         : liveCompleteReport

  const [isDark, setIsDark] = useState(true)
  const [simulationStarted, setSimulationStarted] = useState(TEST_MODE)
  const [showNetwork, setShowNetwork] = useState(false)

  const theme = isDark ? themes.dark : themes.light

  useEffect(() => {
    console.log('agentStatuses:', agentStatuses)
  }, [agentStatuses])

  return (
    <div style={{ ...gridBackground(theme), minHeight: '100vh', color: theme.textPrimary, position: 'relative', overflowX: 'hidden', maxWidth: '100vw' }}>

      {/* Theme toggle — fixed top-right, always visible at zIndex 50 */}
      <button
        onClick={() => setIsDark((d) => !d)}
        title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        style={{
          position: 'fixed',
          top: '1rem',
          right: '1rem',
          zIndex: 50,
          width: 36,
          height: 36,
          borderRadius: '50%',
          background: theme.bgCard,
          border: `1px solid ${theme.borderDefault}`,
          color: theme.textSecondary,
          fontSize: 16,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'background 0.2s, border-color 0.2s',
        }}
      >
        {isDark ? (
          /* Sun — circle + 8 rays */
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke={theme.textMuted} strokeWidth="1.5" strokeLinecap="round">
            <circle cx="8" cy="8" r="3" />
            <line x1="8" y1="1"   x2="8"   y2="2.5" />
            <line x1="8" y1="13.5" x2="8"  y2="15"  />
            <line x1="1" y1="8"   x2="2.5" y2="8"   />
            <line x1="13.5" y1="8" x2="15" y2="8"   />
            <line x1="2.93" y1="2.93" x2="4"    y2="4"    />
            <line x1="12"   y1="12"   x2="13.07" y2="13.07" />
            <line x1="2.93" y1="13.07" x2="4"   y2="12"   />
            <line x1="12"   y1="4"    x2="13.07" y2="2.93" />
          </svg>
        ) : (
          /* Moon — crescent using clip */
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke={theme.textMuted} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M13 10.5A6 6 0 0 1 5.5 3a6 6 0 1 0 7.5 7.5z" />
          </svg>
        )}
      </button>

      {/* ── Section 1 — Input Form (pre-simulation) ── */}
      <AnimatePresence>
        {!simulationStarted && (
          <motion.div
            key="input-form"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            <InputForm
              startSimulation={startSimulation}
              isRunning={isRunning}
              onSimulationStart={() => setSimulationStarted(true)}
              theme={theme}
              isDark={isDark}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Sections 2-7 (post-simulation) ── */}
      {simulationStarted && (
        <motion.div
          key="simulation-view"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          {/* Section 2 — Agent Progress Bar (fixed) */}
          <AgentProgressBar
            agentStatuses={agentStatuses}
            currentAgent={currentAgent}
            isComplete={isComplete}
            theme={theme}
            onViewNetwork={() => setShowNetwork(true)}
            onCancel={() => { reset(); setSimulationStarted(false) }}
          />

          {/* Agent Network Modal */}
          <AgentNetworkModal
            isOpen={showNetwork}
            onClose={() => setShowNetwork(false)}
            agentStatuses={agentStatuses}
            theme={theme}
          />

          {/* Sections 3-7 — Report Dashboard, fades in on completion */}
          <AnimatePresence>
            {isComplete && (
              <motion.div
                key="report-dashboard"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                <ReportDashboard
                  completeReport={completeReport}
                  theme={theme}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  )
}
