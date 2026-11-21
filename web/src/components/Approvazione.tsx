import { ShieldCheck, X } from 'lucide-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import type { Argomenti, ChiamataTool } from '@/api'

/** Human-in-the-loop: l'azione esterna parte solo dopo un «Approva» esplicito. */
export function Approvazione({ chiamata, occupato, onApprova, onRifiuta }: {
  chiamata: ChiamataTool; occupato: boolean
  onApprova: (argomenti: Argomenti) => void; onRifiuta: (motivo: string) => void
}) {
  const [testo, setTesto] = useState(JSON.stringify(chiamata.arguments, null, 2))
  const [motivo, setMotivo] = useState('')
  let errore = ''
  let args: Argomenti = {}
  try { args = JSON.parse(testo) } catch (e) { errore = (e as Error).message }

  return (
    <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-warn/50 bg-surface p-4 shadow-[0_0_40px_-12px_var(--warn)]">
      <div className="flex items-center gap-2 text-sm font-semibold text-warn"><ShieldCheck className="size-4" />Serve la tua approvazione</div>
      <p className="mt-2 text-sm">L'agente vuole eseguire <code className="rounded bg-surface2 px-1.5 py-0.5 font-mono text-xs">{chiamata.name}</code>. Controlla i dati, correggili se serve.</p>
      <textarea value={testo} onChange={(e) => setTesto(e.target.value)} spellCheck={false} rows={10}
        className="mt-3 w-full resize-y rounded-lg border border-line bg-bg p-3 font-mono text-xs outline-none focus:border-accent" />
      {errore && <p className="mt-1 text-xs text-bad">JSON non valido: {errore}</p>}
      <input value={motivo} onChange={(e) => setMotivo(e.target.value)} placeholder="Motivo (se rifiuti)"
        className="mt-2 w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm outline-none focus:border-accent" />
      <div className="mt-3 flex gap-2">
        <button disabled={occupato || !!errore} onClick={() => onApprova(args)}
          className="flex-1 rounded-lg bg-ok px-3 py-2 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-40">Approva</button>
        <button disabled={occupato} onClick={() => onRifiuta(motivo)}
          className="flex items-center gap-1 rounded-lg border border-line px-3 py-2 text-sm transition hover:border-bad hover:text-bad disabled:opacity-40"><X className="size-4" />Rifiuta</button>
      </div>
    </motion.div>
  )
}
