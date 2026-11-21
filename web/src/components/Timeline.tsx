import { ChevronDown } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useState } from 'react'
import type { Passo } from '@/api'
import { cn } from '@/lib'
import { COLORE, ICONE, titolo } from '@/passi'

function Riga({ p, ultimo }: { p: Passo; ultimo: boolean }) {
  const [aperto, setAperto] = useState(p.tipo === 'in_attesa' || p.tipo === 'errore')
  const Icona = ICONE[p.tipo]
  const { ts, run_id: _r, tipo: _t, durata_ms, ...dettagli } = p
  return (
    <motion.li layout initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} className="relative pl-10">
      <span className="absolute top-0 bottom-0 left-[15px] w-px bg-line" />
      <span className={cn('absolute top-1 left-0 grid size-8 place-items-center rounded-full border border-line bg-surface', COLORE[p.tipo])}>
        <Icona className="size-4" />
        {ultimo && <span className="absolute inset-0 animate-ping rounded-full bg-accent/20" />}
      </span>
      <button onClick={() => setAperto(!aperto)} className="w-full rounded-lg px-2 py-1.5 text-left hover:bg-surface2">
        <div className="flex items-start justify-between gap-3">
          <span className="text-sm leading-snug">{titolo(p)}</span>
          <ChevronDown className={cn('mt-0.5 size-4 shrink-0 text-muted transition', aperto && 'rotate-180')} />
        </div>
        <div className="mt-0.5 font-mono text-[11px] text-muted">
          {ts.slice(11, 23)}{durata_ms != null && ` · ${durata_ms} ms`}
        </div>
      </button>
      <AnimatePresence initial={false}>
        {aperto && (
          <motion.pre
            initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="mx-2 mb-3 overflow-auto rounded-lg border border-line bg-bg p-3 font-mono text-[11px] leading-relaxed text-muted"
          >
            {JSON.stringify(dettagli, null, 2)}
          </motion.pre>
        )}
      </AnimatePresence>
    </motion.li>
  )
}

export function Timeline({ passi }: { passi: Passo[] }) {
  if (!passi.length) return <p className="py-10 text-center text-sm text-muted">Nessun passo ancora. Premi «Elabora».</p>
  return (
    <ol className="flex flex-col pb-4">
      {passi.map((p, i) => <Riga key={`${p.ts}-${i}`} p={p} ultimo={i === passi.length - 1} />)}
    </ol>
  )
}
