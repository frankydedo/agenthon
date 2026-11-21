import { ChevronDown } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useState } from 'react'
import type { Passo } from '@/api'
import { spiega } from '@/azioni'
import { cn } from '@/lib'
import { COLORE, ICONE } from '@/passi'

function Riga({ p, numero, ultimo }: { p: Passo; numero: number; ultimo: boolean }) {
  const [aperto, setAperto] = useState(false)
  const Icona = ICONE[p.tipo]
  const { titolo, dettaglio } = spiega(p)
  const { ts, run_id: _r, tipo: _t, durata_ms, ...tecnici } = p
  return (
    <motion.li layout initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 380, damping: 32 }}
      className={cn('relative rounded-xl border p-3 transition-colors', ultimo ? 'border-accent/70 bg-accent/10 shadow-[0_0_30px_-10px_var(--accent)]' : 'border-line bg-surface')}>
      <button onClick={() => setAperto(!aperto)} className="flex w-full items-start gap-3 text-left">
        <span className={cn('relative grid size-8 shrink-0 place-items-center rounded-full border border-line bg-bg', COLORE[p.tipo])}>
          <Icona className="size-4" />
          {ultimo && <span className="absolute inset-0 animate-ping rounded-full bg-accent/25" />}
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2 text-[11px] text-muted">
            <span className="font-mono">#{numero}</span>
            {ultimo && <span className="rounded bg-accent px-1.5 py-px font-semibold text-bg">ULTIMO</span>}
            <span className="font-mono">{ts.slice(11, 19)}{durata_ms != null && ` · ${(durata_ms / 1000).toFixed(1)} s`}</span>
          </span>
          <span className="mt-0.5 block text-sm leading-snug font-medium">{titolo}</span>
          {dettaglio && <span className="mt-0.5 block text-[13px] leading-snug whitespace-pre-wrap text-muted">{dettaglio}</span>}
        </span>
        <ChevronDown className={cn('mt-1 size-4 shrink-0 text-muted transition', aperto && 'rotate-180')} />
      </button>
      <AnimatePresence initial={false}>
        {aperto && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <p className="mt-3 mb-1 text-[11px] font-medium tracking-wide text-muted uppercase">Dati tecnici</p>
            <pre className="overflow-auto rounded-lg border border-line bg-bg p-3 font-mono text-[11px] leading-relaxed text-muted">{JSON.stringify(tecnici, null, 2)}</pre>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.li>
  )
}

/** Il flusso delle operazioni: l'ultimo passo è SEMPRE in alto, così non serve scorrere. */
export function Timeline({ passi }: { passi: Passo[] }) {
  if (!passi.length) return <p className="py-10 text-center text-sm text-muted">L'agente non ha ancora lavorato su questa richiesta. Premi «Avvia l'agente».</p>
  const ordinati = passi.map((p, i) => ({ p, n: i + 1 })).reverse()
  return (
    <ol className="flex flex-col gap-2">
      {ordinati.map(({ p, n }) => <Riga key={`${p.ts}-${n}`} p={p} numero={n} ultimo={n === passi.length} />)}
    </ol>
  )
}
