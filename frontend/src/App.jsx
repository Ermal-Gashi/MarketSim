import useSimulation from './hooks/useSimulation'
// import InputForm from './components/InputForm'
// import AgentProgressBar from './components/AgentProgressBar'
// import AgentNetworkModal from './components/AgentNetworkModal'
// import HeroMap from './components/HeroMap'
// import RadarChart from './components/RadarChart'
// import PersonaCards from './components/PersonaCards'
// import ObstacleMatrix from './components/ObstacleMatrix'
// import EntryRoadmap from './components/EntryRoadmap'
// import VerdictSummary from './components/VerdictSummary'

function App() {
  return (
    <div className="bg-gray-950 min-h-screen text-white">
      <div className="flex items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold tracking-tight">MarketSim</h1>
      </div>

      {/* Section 1 — Input Form */}
      <div>{/* <InputForm /> */}</div>

      {/* Section 2 — Agent Progress */}
      <div>{/* <AgentProgressBar /> <AgentNetworkModal /> */}</div>

      {/* Section 3 — Hero Visuals */}
      <div>{/* <HeroMap /> <RadarChart /> */}</div>

      {/* Section 4 — Persona Cards */}
      <div>{/* <PersonaCards /> */}</div>

      {/* Section 5 — Obstacle Matrix */}
      <div>{/* <ObstacleMatrix /> */}</div>

      {/* Section 6 — Entry Roadmap */}
      <div>{/* <EntryRoadmap /> */}</div>

      {/* Section 7 — Verdict Summary */}
      <div>{/* <VerdictSummary /> */}</div>
    </div>
  )
}

export default App
