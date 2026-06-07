import { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import * as d3 from 'd3'

// ── constants ─────────────────────────────────────────────────────────────────

const GEOJSON_URL = 'https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson'

const MAP_HEIGHT = 380  // Fix 2 — larger map height

const VERDICT_COLORS = {
  'GO':          '#4DBBAA',
  'CAUTIOUS GO': '#C9A84C',
  'NO-GO':       '#C46B8A',
}

const OUTCOME_COLORS = {
  converted:  '#4DBBAA',
  evaluating: '#C9A84C',
  abandoned:  '#C46B8A',
}

function verdictColor(verdict) {
  if (!verdict) return '#6B6B78'
  const v = verdict.toUpperCase()
  return VERDICT_COLORS[v] ?? '#6B6B78'
}

// ── corner bracket component ──────────────────────────────────────────────────

function CornerBrackets({ color, size = 20, thickness = 2.5 }) {
  // corners live inside the pulsing parent wrapper — no separate animation needed
  const s = { position: 'absolute', width: size, height: size }
  const b = `${thickness}px solid ${color}`
  return (
    <>
      <div style={{ ...s, top: 0, left: 0,  borderTop: b, borderLeft: b }} />
      <div style={{ ...s, top: 0, right: 0, borderTop: b, borderRight: b }} />
      <div style={{ ...s, bottom: 0, left: 0,  borderBottom: b, borderLeft: b }} />
      <div style={{ ...s, bottom: 0, right: 0, borderBottom: b, borderRight: b }} />
    </>
  )
}

// ── tooltip ───────────────────────────────────────────────────────────────────

function Tooltip({ dot, theme }) {
  if (!dot) return null
  const x = dot.screenX + 12
  const y = dot.screenY - 8
  return (
    <div style={{
      position: 'fixed', left: x, top: y,
      background: theme.bgCard,
      border: `1px solid ${theme.borderDefault}`,
      borderRadius: 8, padding: '8px 12px',
      fontSize: 11, color: theme.textSecondary,
      zIndex: 200, pointerEvents: 'none',
      boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
      maxWidth: 200,
    }}>
      <p style={{ margin: '0 0 2px', fontWeight: 600, color: theme.textPrimary, fontSize: 12 }}>{dot.display_name}</p>
      <p style={{ margin: '0 0 2px', color: theme.textSecondary }}>{dot.job_title}</p>
      <p style={{ margin: '0 0 4px' }}>
        <span style={{ color: OUTCOME_COLORS[dot.conversion_outcome] ?? theme.textMuted }}>
          {dot.conversion_outcome}
        </span>
      </p>
      <p style={{ margin: 0, color: theme.textMuted, fontStyle: 'italic', fontSize: 10 }}>{dot.outcome_reason}</p>
    </div>
  )
}

// ── main component ────────────────────────────────────────────────────────────

export default function HeroMap({ agent6Output, agent7Output, targetMarket, theme, hoveredArchetype }) {
  const svgRef      = useRef(null)
  const [tooltip, setTooltip] = useState(null)
  const timeoutsRef = useRef([])
  // store instances in a ref so the archetype-hover effect can access them without re-running the map effect
  const instancesRef = useRef([])

  const verdict    = agent6Output?.verdict
  const confidence = agent6Output?.confidence_score
  const reason     = agent6Output?.verdict_reason
  const instances  = agent7Output?.instances || []
  const vColor     = verdictColor(verdict)

  // ── D3 map render + dot spawning ──
  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return

    // clear previous renders and pending timeouts
    d3.select(svg).selectAll('*').remove()
    timeoutsRef.current.forEach(clearTimeout)
    timeoutsRef.current = []
    instancesRef.current = instances

    const width  = svg.clientWidth || 480
    const height = MAP_HEIGHT

    const g = d3.select(svg)
      .attr('width', width)
      .attr('height', height)
      .append('g')

    fetch(GEOJSON_URL)
      .then((r) => r.json())
      .then((world) => {
        // find matching country feature
        const target = (targetMarket || '').toLowerCase()
        const feature = world.features.find((f) => {
          const n = (f.properties.name || '').toLowerCase()
          return n === target || n.includes(target) || target.includes(n)
        })

        const features = feature ? [feature] : world.features.slice(0, 1)

        // Fix 1 — fitSize on the matched country's GeoJSON feature so the
        // projection is scaled/centered specifically for that country
        const projection = d3.geoMercator()
          .fitSize([width, height], { type: 'FeatureCollection', features })

        const path = d3.geoPath().projection(projection)

        // debug — verify the projection lands within SVG bounds for this country
        console.log('HeroMap: matched feature for target market:', target, '→', feature?.properties?.name)
        console.log('HeroMap: projected sample (Karachi 24.8607, 67.0011):', projection([67.0011, 24.8607]))
        console.log('HeroMap: first 5 instances projected:', instances.slice(0, 5).map((inst) => {
          const p = projection([inst.lng, inst.lat])
          return { city: inst.city, lat: inst.lat, lng: inst.lng, projected: p }
        }))

        // draw country — Fix 1: fill matches card background (no nested inner box)
        g.selectAll('path')
          .data(features)
          .enter().append('path')
          .attr('d', path)
          .attr('fill', theme.bgCard)
          .attr('stroke', theme.bgPage.startsWith('#F') ? '#8A8A95' : '#4A4A5A')
          .attr('stroke-width', theme.bgPage.startsWith('#F') ? 2 : 2.5)

        // dedicated layer for dots — appended AFTER the country path so dots
        // always render on top and are never hidden/clipped behind the silhouette
        const dotLayer = g.append('g').attr('class', 'dot-layer')

        // spawn dots after country renders
        instances.forEach((inst) => {
          const tid = setTimeout(() => {
            if (!svgRef.current) return
            const projected = projection([inst.lng, inst.lat])
            if (!projected) return
            const [px, py] = projected

            const circle = dotLayer.append('circle')
              .attr('cx', px)
              .attr('cy', py)
              .attr('r', 0)
              .attr('fill', OUTCOME_COLORS[inst.conversion_outcome] || theme.textMuted)
              .attr('fill-opacity', 0.75)
              .attr('stroke', 'none')
              .attr('data-archetype', inst.archetype_name || '')  // tag for hover filtering
              .style('cursor', 'pointer')

            // animate in
            circle.transition().duration(300).attr('r', 4)

            // tooltip handlers
            circle.on('mouseenter', (event) => {
              setTooltip({
                ...inst,
                screenX: event.clientX,
                screenY: event.clientY,
              })
            })
            circle.on('mouseleave', () => setTooltip(null))
          }, inst.spawn_delay_ms || 0)

          timeoutsRef.current.push(tid)
        })
      })
      .catch(() => {
        d3.select(svg).append('text')
          .attr('x', width / 2).attr('y', height / 2)
          .attr('text-anchor', 'middle')
          .attr('fill', theme.textMuted)
          .attr('font-size', 12)
          .text('Map unavailable')
      })

    return () => {
      timeoutsRef.current.forEach(clearTimeout)
    }
  }, [targetMarket, instances, theme])

  // ── Fix 4: archetype hover — update dot opacity + radius via D3 selection ──
  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return

    const circles = d3.select(svg).selectAll('circle')

    if (!hoveredArchetype) {
      // reset all dots to normal
      circles
        .transition().duration(150)
        .attr('r', 4)
        .attr('fill-opacity', 0.75)
    } else {
      // highlight matching, dim non-matching
      circles
        .transition().duration(150)
        .attr('r', (d, i, nodes) => {
          const el = nodes[i]
          return el.getAttribute('data-archetype') === hoveredArchetype ? 6 : 4
        })
        .attr('fill-opacity', (d, i, nodes) => {
          const el = nodes[i]
          return el.getAttribute('data-archetype') === hoveredArchetype ? 1 : 0.15
        })
    }
  }, [hoveredArchetype])

  // ── empty state ──
  if (!verdict && !confidence) {
    return (
      <div style={{
        height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: theme.bgCard, border: `1px solid ${theme.borderDefault}`,
        borderRadius: 12, fontSize: 13, color: theme.textMuted,
      }}>
        Awaiting simulation data
      </div>
    )
  }

  return (
    <>
      {/* verdict-pulse keyframe — applied to verdict stamp wrapper so corners + text breathe together */}
      <style>{`
        @keyframes verdict-pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.6; }
        }
      `}</style>

      {/* ── Fix 1: single card container, no nested inner box ── */}
      <div style={{
        background: theme.bgCard,
        border: `1px solid ${theme.borderDefault}`,
        borderRadius: 12,
        padding: 20,
        height: '100%',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        overflowX: 'clip',
        overflowY: 'visible',
      }}>

        {/* ── Verdict stamp — wrapper pulses so corners + text animate together ── */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 4, width: '100%' }}>
          <div style={{
            position: 'relative',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '12px 28px',
            animation: 'verdict-pulse 2.5s ease-in-out infinite',
          }}>
            <CornerBrackets color={vColor} size={20} thickness={2.5} />
            <span style={{
              fontSize: 36, fontWeight: 700, letterSpacing: '0.15em',
              textTransform: 'uppercase', color: vColor,
            }}>
              {verdict}
            </span>
          </div>

          {confidence != null && (
            <p style={{ fontSize: 13, color: theme.textSecondary, margin: '4px 0 0' }}>
              Confidence: {confidence} / 100
            </p>
          )}

          {reason && (
            <p style={{
              fontSize: 12, color: theme.textMuted, fontStyle: 'italic',
              margin: '4px 24px 0', textAlign: 'center',
              display: '-webkit-box', WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical', overflow: 'hidden',
            }}>
              {reason}
            </p>
          )}
        </div>

        {/* ── Fix 1 + 2: SVG sits directly in card, no inner wrapping div, height 380px ── */}
        <div style={{ position: 'relative', width: '100%', marginTop: 16, flex: 1 }}>
          <svg
            ref={svgRef}
            style={{ width: '100%', height: MAP_HEIGHT, display: 'block', overflow: 'visible' }}
          />
          <Tooltip dot={tooltip} theme={theme} />
        </div>

        {/* ── Dot legend — inside card at bottom, separated by top border ── */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 20,
          width: '100%',
          marginTop: 12,
          paddingTop: 12,
          borderTop: `1px solid ${theme.borderDefault}`,
        }}>
          {[
            { label: 'Converted',  color: OUTCOME_COLORS.converted  },
            { label: 'Evaluating', color: OUTCOME_COLORS.evaluating },
            { label: 'Abandoned',  color: OUTCOME_COLORS.abandoned  },
          ].map(({ label, color }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: color, display: 'inline-block' }} />
              <span style={{ fontSize: 11, color: theme.textMuted }}>{label}</span>
            </div>
          ))}
        </div>

      </div>
    </>
  )
}

HeroMap.propTypes = {
  agent6Output:     PropTypes.object,
  agent7Output:     PropTypes.object,
  targetMarket:     PropTypes.string,
  theme:            PropTypes.object.isRequired,
  hoveredArchetype: PropTypes.string,
}
