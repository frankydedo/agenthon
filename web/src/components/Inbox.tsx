import { Paperclip } from 'lucide-react'
import { motion } from 'motion/react'
import type { Richiesta } from '@/api'
import { cn } from '@/lib'
import { STATO } from '@/passi'

export function Inbox({ richieste, selezionata, onSeleziona }: {
  richieste: Richiesta[]; selezionata: string | null; onSeleziona: (id: string) => void
}) {
  return (
    <ul className="flex flex-col gap-2">
      {richieste.map((r, i) => {
        const s = STATO[r.stato ?? 'nuovo']
        return (
          <motion.li key={r.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
            <button
              onClick={() => onSeleziona(r.id)}
              className={cn(
                'w-full rounded-xl border p-3 text-left transition hover:border-accent/60 hover:bg-surface2',
                selezionata === r.id ? 'border-accent bg-surface2 shadow-[0_0_0_1px_var(--accent)]' : 'border-line bg-surface',
              )}
            >
              <div className="flex items-center justify-between gap-2 text-xs text-muted">
                <span className="truncate">{r.da}</span>
                <span className="flex shrink-0 items-center gap-1.5">
                  <span className={cn('size-2 rounded-full', s.colore, r.stato === 'in_attesa' && 'animate-pulse')} />
                  {s.etichetta}
                </span>
              </div>
              <div className="mt-1 line-clamp-2 text-sm font-medium">{r.oggetto}</div>
              {r.allegati.length > 0 && (
                <div className="mt-1.5 flex items-center gap-1 text-xs text-muted"><Paperclip className="size-3" />{r.allegati.length}</div>
              )}
            </button>
          </motion.li>
        )
      })}
    </ul>
  )
}
