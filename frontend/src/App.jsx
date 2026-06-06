import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import useSimulation from './hooks/useSimulation'
import InputForm from './components/InputForm'
// import AgentProgressBar from './components/AgentProgressBar'
// import AgentNetworkModal from './components/AgentNetworkModal'
// import HeroMap from './components/HeroMap'
// import RadarChart from './components/RadarChart'
// import PersonaCards from './components/PersonaCards'
// import ObstacleMatrix from './components/ObstacleMatrix'
// import EntryRoadmap from './components/EntryRoadmap'
// import VerdictSummary from './components/VerdictSummary'

const gridBackground = {
  backgroundColor: '#0D0D10',
  backgroundImage: `
    linear-gradient(#1E1E28 1px, transparent 1px),
    linear-gradient(90deg, #1E1E28 1px, transparent 1px),
    linear-gradient(#14141A 1px, transparent 1px),
    linear-gradient(90deg, #14141A 1px, transparent 1px)
  `,
  backgroundSize: '150px 150px, 150px 150px, 30px 30px, 30px 30px',
  backgroundPosition: '-1px -1px, -1px -1px, -1px -1px, -1px -1px',
}

export default function App() {
  const {
    agentStatuses,
    isRunning,
    isComplete,
    completeReport,
    error,
    currentAgent,
    startSimulation,
    reset,
  } = useSimulation()

  const [simulationStarted, setSimulationStarted] = useState(false)

  useEffect(() => {
    console.log('agentStatuses:', agentStatuses)
  }, [agentStatuses])

  return (
    <div style={{ ...gridBackground, minHeight: '100vh', color: 'white' }}>
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
            />
          </motion.div>
        )}
      </AnimatePresence>

      {simulationStarted && (
        <motion.div
          key="post-input"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-center min-h-screen text-slate-400 text-sm"
        >
          {/* Section 2 — Agent Progress */}
          <div>Agent progress will appear here</div>

          {/* Section 3 — Hero Visuals */}
          {/* Section 4 — Persona Cards */}
          {/* Section 5 — Obstacle Matrix */}
          {/* Section 6 — Entry Roadmap */}
          {/* Section 7 — Verdict Summary */}
        </motion.div>
      )}
    </div>
  )
}
