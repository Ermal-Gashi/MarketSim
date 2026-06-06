import { useState, useRef, useCallback, useEffect } from 'react'

const AGENT_NAMES = [
  'Product Analyst',
  'Market Data Fetcher',
  'Cultural Fit Scorer',
  'Persona Generator',
  'Obstacle Detector',
  'Synthesizer',
  'Simulation Layer',
]

const initialAgentStatuses = AGENT_NAMES.map((name, i) => ({
  agentNumber: i + 1,
  name,
  status: 'waiting',
  output: null,
  error: null,
}))

export default function useSimulation() {
  const [agentStatuses, setAgentStatuses] = useState(initialAgentStatuses)
  const [isRunning, setIsRunning] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [completeReport, setCompleteReport] = useState(null)
  const [error, setError] = useState(null)
  const [currentAgent, setCurrentAgent] = useState(null)

  const esRef = useRef(null)

  const closeConnection = useCallback(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
  }, [])

  const reset = useCallback(() => {
    closeConnection()
    setAgentStatuses(initialAgentStatuses)
    setIsRunning(false)
    setIsComplete(false)
    setCompleteReport(null)
    setError(null)
    setCurrentAgent(null)
  }, [closeConnection])

  const startSimulation = useCallback((productDescription, currentMarket, targetMarket) => {
    closeConnection()

    const params = new URLSearchParams({
      product_description: productDescription,
      current_market: currentMarket,
      target_market: targetMarket,
    })

    const es = new EventSource(`/api/simulate?${params.toString()}`)
    esRef.current = es

    setIsRunning(true)
    setIsComplete(false)
    setCompleteReport(null)
    setError(null)
    setCurrentAgent(null)
    setAgentStatuses(initialAgentStatuses)

    es.onmessage = (event) => {
      let data
      try {
        data = JSON.parse(event.data)
      } catch {
        return
      }

      const agentIndex = data.agent - 1

      if (data.status === 'running') {
        setCurrentAgent(data.agent)
        setAgentStatuses((prev) =>
          prev.map((a, i) =>
            i === agentIndex ? { ...a, status: 'running' } : a
          )
        )
      } else if (data.status === 'done') {
        setAgentStatuses((prev) =>
          prev.map((a, i) =>
            i === agentIndex ? { ...a, status: 'done', output: data.output ?? null } : a
          )
        )

        if (data.final === true) {
          setIsComplete(true)
          setIsRunning(false)
          setCurrentAgent(null)
          setCompleteReport(data.complete_report ?? null)
          closeConnection()
        }
      } else if (data.status === 'error') {
        const msg = data.error ?? 'An unknown error occurred'
        setAgentStatuses((prev) =>
          prev.map((a, i) =>
            i === agentIndex ? { ...a, status: 'error', error: msg } : a
          )
        )
        setError(msg)
        setIsRunning(false)
        closeConnection()
      }
    }

    es.onerror = () => {
      setError('Connection lost — please try again')
      setIsRunning(false)
      closeConnection()
    }
  }, [closeConnection])

  // Cleanup on unmount
  useEffect(() => {
    return () => closeConnection()
  }, [closeConnection])

  return {
    agentStatuses,
    isRunning,
    isComplete,
    completeReport,
    error,
    currentAgent,
    startSimulation,
    reset,
  }
}
