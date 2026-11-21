import { Background, Controls, MarkerType, ReactFlow, type Edge, type Node } from '@xyflow/react'
import { useMemo } from 'react'
import type { Passo } from '@/api'
import { titolo } from '@/passi'

const CORSIA: Record<Passo['tipo'], number> = {
  inizio: 1, llm: 0, tool: 1, in_attesa: 2, approvato: 2, rifiutato: 2, modificato: 2, fine: 0, errore: 1,
}
const COLORE: Record<Passo['tipo'], string> = {
  inizio: 'var(--info)', llm: 'var(--accent)', tool: 'var(--text)', in_attesa: 'var(--warn)', approvato: 'var(--ok)',
  rifiutato: 'var(--bad)', modificato: 'var(--warn)', fine: 'var(--ok)', errore: 'var(--bad)',
}

/** Il ragionamento dell'agente come grafo: in alto il modello, al centro i tool, in basso l'umano. */
export function Grafo({ passi }: { passi: Passo[] }) {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = passi.map((p, i) => ({
      id: String(i), position: { x: i * 230, y: CORSIA[p.tipo] * 130 }, draggable: false,
      data: { label: titolo(p).slice(0, 70) },
      style: {
        width: 200, fontSize: 12, borderRadius: 12, padding: 10, color: 'var(--text)',
        background: 'var(--surface)', border: `1.5px solid ${COLORE[p.tipo]}`,
        boxShadow: i === passi.length - 1 ? `0 0 24px color-mix(in oklab, ${COLORE[p.tipo]} 45%, transparent)` : 'none',
      },
    }))
    const edges: Edge[] = passi.slice(1).map((_, i) => ({
      id: `e${i}`, source: String(i), target: String(i + 1), animated: i === passi.length - 2,
      markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--muted)' }, style: { stroke: 'var(--muted)' },
    }))
    return { nodes, edges }
  }, [passi])

  if (!passi.length) return <p className="py-10 text-center text-sm text-muted">Il grafo appare quando l'agente parte.</p>
  return (
    <div className="h-[420px] overflow-hidden rounded-xl border border-line">
      <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.2, maxZoom: 1 }}
        nodesConnectable={false} proOptions={{ hideAttribution: true }}>
        <Background gap={24} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
