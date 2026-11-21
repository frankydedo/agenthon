import { Code2, Mail, ShieldCheck, X } from 'lucide-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import type { Argomenti, ChiamataTool } from '@/api'
import { descrivi } from '@/azioni'

/** Human-in-the-loop: l'azione esterna parte solo dopo un «Approva» esplicito.
 *  La persona vede una descrizione in italiano; il JSON è dietro un pulsante. */
export function Approvazione({ chiamata, motivazione, clienti, occupato, onApprova, onRifiuta }: {
  chiamata: ChiamataTool; motivazione?: string; clienti: Record<string, unknown>[]; occupato: boolean
  onApprova: (argomenti: Argomenti) => void; onRifiuta: (motivo: string) => void
}) {
  const d = descrivi(chiamata, clienti)
  const [tecnico, setTecnico] = useState(false)
  const [testo, setTesto] = useState(JSON.stringify(chiamata.arguments, null, 2))
  const [motivo, setMotivo] = useState('')
  let errore = ''
  let args: Argomenti = {}
  try { args = JSON.parse(testo) } catch (e) { errore = (e as Error).message }

  return (
    <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-warn/60 bg-surface p-4 shadow-[0_0_40px_-12px_var(--warn)]">
      <div className="flex items-center gap-2 text-sm font-semibold text-warn"><ShieldCheck className="size-4" />Serve la tua approvazione</div>
      <h3 className="mt-2 text-base font-semibold">{d.titolo}</h3>
      {motivazione && <p className="mt-1 text-sm text-muted"><span className="font-medium text-fg">Perché: </span>{motivazione}</p>}

      {d.email && (
        <div className="mt-3 overflow-hidden rounded-xl border border-line bg-bg">
          <div className="flex items-center gap-2 border-b border-line bg-surface2 px-3 py-2 text-xs text-muted"><Mail className="size-3.5" />Anteprima dell'email</div>
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 px-3 pt-3 text-sm">
            <dt className="text-muted">A</dt><dd className="font-medium break-all">{d.email.a}</dd>
            <dt className="text-muted">Oggetto</dt><dd className="font-medium">{d.email.oggetto}</dd>
          </dl>
          <p className="px-3 py-3 text-sm whitespace-pre-wrap">{d.email.corpo}</p>
        </div>
      )}
      {d.campi.length > 0 && (
        <dl className="mt-3 divide-y divide-line rounded-xl border border-line bg-bg text-sm">
          {d.campi.map((c) => (
            <div key={c.etichetta} className="grid grid-cols-[120px_1fr] gap-3 px-3 py-2"><dt className="text-muted">{c.etichetta}</dt><dd className="font-medium break-words">{c.valore}</dd></div>
          ))}
        </dl>
      )}

      <p className="mt-3 text-xs text-muted"><span className="font-medium text-ok">Se approvi:</span> {d.effetto} <span className="font-medium text-bad">Se rifiuti:</span> non succede nulla e l'agente propone un'alternativa.</p>

      <button onClick={() => setTecnico(!tecnico)} className="mt-3 flex items-center gap-1.5 text-xs text-muted transition hover:text-fg">
        <Code2 className="size-3.5" />{tecnico ? 'Nascondi' : 'Mostra'} dati tecnici (per utenti esperti)</button>
      {tecnico && (
        <div className="mt-2">
          <textarea value={testo} onChange={(e) => setTesto(e.target.value)} spellCheck={false} rows={9}
            className="w-full resize-y rounded-lg border border-line bg-bg p-3 font-mono text-xs outline-none focus:border-accent" />
          <p className="text-[11px] text-muted">Puoi correggere i valori: l'azione userà questi dati.</p>
          {errore && <p className="mt-1 text-xs text-bad">JSON non valido: {errore}</p>}
        </div>
      )}

      <input value={motivo} onChange={(e) => setMotivo(e.target.value)} placeholder="Motivo del rifiuto (facoltativo)"
        className="mt-3 w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm outline-none focus:border-accent" />
      <div className="mt-3 flex gap-2">
        <button disabled={occupato || !!errore} onClick={() => onApprova(args)}
          className="flex-1 rounded-lg bg-ok px-3 py-2.5 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-40">Approva</button>
        <button disabled={occupato} onClick={() => onRifiuta(motivo)}
          className="flex items-center gap-1 rounded-lg border border-line px-3 py-2.5 text-sm transition hover:border-bad hover:text-bad disabled:opacity-40"><X className="size-4" />Rifiuta</button>
      </div>
    </motion.div>
  )
}
