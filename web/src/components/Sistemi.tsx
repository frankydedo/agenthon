import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { api } from '@/api'
import { cn } from '@/lib'

type Riga = Record<string, unknown>
const SCHEDE = [['pratiche', 'Pratiche'], ['fatture', 'Fatture registrate'], ['email_inviate', 'Email inviate'], ['clienti', 'Clienti']] as const

function Tabella({ righe }: { righe: Riga[] }) {
  if (!righe.length) return <p className="py-6 text-center text-sm text-muted">Vuoto.</p>
  const colonne = Object.keys(righe[0])
  return (
    <div className="overflow-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-muted"><tr>{colonne.map((c) => <th key={c} className="px-3 py-2 font-medium">{c}</th>)}</tr></thead>
        <tbody>
          {righe.map((r, i) => (
            <tr key={i} className="border-t border-line">{colonne.map((c) => <td key={c} className="max-w-72 truncate px-3 py-2">{String(r[c] ?? '')}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Cosa è cambiato davvero nei sistemi dello studio (simulati). */
export function Sistemi({ aggiorna }: { aggiorna: number }) {
  const [scheda, setScheda] = useState<(typeof SCHEDE)[number][0]>('pratiche')
  const { data } = useQuery({ queryKey: ['sistemi', aggiorna], queryFn: api.sistemi })
  return (
    <section className="rounded-2xl border border-line bg-surface">
      <div className="flex gap-1 border-b border-line p-2">
        {SCHEDE.map(([k, nome]) => (
          <button key={k} onClick={() => setScheda(k)}
            className={cn('rounded-lg px-3 py-1.5 text-sm transition', scheda === k ? 'bg-surface2 text-fg' : 'text-muted hover:text-fg')}>
            {nome}{data && <span className="ml-1.5 text-xs text-muted">{data[k].length}</span>}
          </button>
        ))}
      </div>
      <Tabella righe={(data?.[scheda] ?? []) as Riga[]} />
    </section>
  )
}
