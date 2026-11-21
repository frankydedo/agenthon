import { useQuery } from '@tanstack/react-query'
import { Brain, Check, CheckCircle2, ChevronDown, Eye, FileText, Hand, Loader2, Mail, Paperclip, ShieldCheck, Wrench } from 'lucide-react'
import { motion } from 'motion/react'
import { Fragment, useEffect, useRef, useState, type ReactNode } from 'react'
import { api, type Argomenti, type Dettaglio, type Passo, type Richiesta } from '@/api'
import { frase, leggiEsito, nomeTool } from '@/azioni'
import { costruisciFasi, type Fase, type Operazione } from '@/fasi'
import { cn } from '@/lib'
import { Approvazione } from './Approvazione'
import { GeneraRichiesta } from './GeneraRichiesta'
import { Inbox } from './Inbox'

interface Props {
  richieste: Richiesta[]; selezionata: string | null; onSeleziona: (id: string) => void
  dettaglio: Dettaglio | undefined; passi: Passo[]; clienti: Record<string, unknown>[]
  occupato: boolean; inCorso: boolean; errore?: string
  onElabora: () => void; onApprova: (a: Argomenti) => void; onRifiuta: (m: string) => void
}

/** Schermata «Come ragiona l'agente»: la stessa richiesta raccontata come una storia, dall'arrivo all'esito. */
export function Ragionamento(p: Props) {
  const fondo = useRef<HTMLDivElement>(null)
  const run = p.dettaglio?.run
  const email = p.dettaglio?.richiesta
  const fasi = costruisciFasi(p.passi)
  const info = useQuery({ queryKey: ['agente'], queryFn: api.agente })
  const esterni = new Set(info.data?.strumenti.filter((s) => s.esterno).map((s) => s.nome))
  const motivazione = [...p.passi].reverse().find((x) => x.tipo === 'llm' && x.testo)?.testo as string | undefined

  // Segue il lavoro dell'agente: a ogni nuovo passo scorre in fondo alla storia.
  useEffect(() => { if (p.passi.length) fondo.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [p.passi.length, run?.stato])

  return (
    <main className="grid flex-1 gap-4 lg:grid-cols-[300px_1fr]">
      <aside className="flex flex-col gap-3 lg:sticky lg:top-4 lg:self-start">
        <GeneraRichiesta onGenerata={p.onSeleziona} />
        <h2 className="text-xs font-medium tracking-wide text-muted uppercase">Richieste in arrivo</h2>
        <Inbox richieste={p.richieste} selezionata={p.selezionata} onSeleziona={p.onSeleziona} />
      </aside>

      <section className="flex min-w-0 flex-col gap-4">
        {!email ? (
          <div className="rounded-2xl border border-line bg-surface p-8 text-center text-sm text-muted">
            Genera una richiesta a sinistra: qui vedrai, passo dopo passo, <b className="text-fg">cosa è arrivato</b>, <b className="text-fg">come ragiona l'agente</b>, <b className="text-fg">cosa decide e perché</b>.
          </div>
        ) : (
          <>
            <Percorso fasi={fasi} run={run?.stato} />

            <Capitolo n="1" titolo="Cosa è arrivato" sotto="L'email del cliente, esattamente come è entrata nella casella dello studio.">
              <Arrivo email={email} input={p.passi.find((x) => x.tipo === 'inizio')?.input as string | undefined} />
            </Capitolo>

            <Capitolo n="2" titolo="Chi è l'agente e cosa può fare" sotto="Le istruzioni che ha ricevuto e gli strumenti a disposizione. Quelli «da approvare» non può usarli da solo.">
              <Agente info={info.data} />
            </Capitolo>

            <Capitolo n="3" titolo="Come ragiona, passo dopo passo" sotto="A ogni giro l'agente pensa, decide cosa fare e vede il risultato. Qui li vedi tutti, in ordine.">
              <div className="mb-3 flex items-center gap-2">
                <button disabled={p.occupato} onClick={p.onElabora}
                  className="rounded-lg bg-accent px-3.5 py-2 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-50">
                  {p.inCorso ? 'In corso…' : run ? 'Rielabora' : 'Avvia l\'agente'}</button>
                {p.inCorso && <span className="flex items-center gap-1.5 text-sm text-muted"><Loader2 className="size-4 animate-spin" />L'agente sta lavorando…</span>}
              </div>
              {p.errore && <div className="mb-3 rounded-xl border border-bad/50 bg-bad/10 p-3 text-sm text-bad">{p.errore}</div>}
              {!fasi.length ? <p className="text-sm text-muted">L'agente non ha ancora lavorato su questa richiesta.</p> : (
                <ol className="flex flex-col gap-3">
                  {fasi.map((f, i) => <FaseCard key={f.llm.ts} f={f} n={i + 1} prima={i === 0} ultima={i === fasi.length - 1 && run?.stato === 'completato'} esterni={esterni} />)}
                </ol>
              )}
            </Capitolo>

            {run?.stato === 'in_attesa' && run.in_attesa_di && (
              <Capitolo n="4" titolo="Ora tocca a te" sotto="L'agente ha deciso un'azione che cambia qualcosa fuori dal programma: non la esegue senza il tuo ok.">
                <Approvazione key={run.in_attesa_di.id} chiamata={run.in_attesa_di} motivazione={motivazione} clienti={p.clienti}
                  occupato={p.occupato} onApprova={p.onApprova} onRifiuta={p.onRifiuta} />
              </Capitolo>
            )}

            {(run?.stato === 'completato' || run?.stato === 'errore') && (
              <Capitolo n="5" titolo="Come è finita" sotto="Cosa è stato fatto davvero e perché, nelle parole dell'agente.">
                <Esito fasi={fasi} passi={p.passi} finale={run.risposta_finale} errore={run.errore} />
              </Capitolo>
            )}
          </>
        )}
        <div ref={fondo} />
      </section>
    </main>
  )
}

function Capitolo({ n, titolo, sotto, children }: { n: string; titolo: string; sotto: string; children: ReactNode }) {
  return (
    <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-line bg-surface p-4">
      <header className="mb-3 flex items-start gap-3">
        <span className="grid size-7 shrink-0 place-items-center rounded-full bg-accent/15 text-sm font-semibold text-accent">{n}</span>
        <div><h2 className="font-semibold">{titolo}</h2><p className="text-sm text-muted">{sotto}</p></div>
      </header>
      {children}
    </motion.section>
  )
}

/** La barra con le tappe del percorso: a che punto siamo. */
function Percorso({ fasi, run }: { fasi: Fase[]; run?: string }) {
  const ops = fasi.flatMap((f) => f.operazioni)
  const tappe = [
    ['Arrivo', true],
    ['Comprensione', fasi.length > 0],
    ['Raccolta dati', ops.some((o) => o.esito && !o.attesa)],
    ['Azioni e approvazione', ops.some((o) => o.attesa)],
    ['Esito', run === 'completato' || run === 'errore'],
  ] as const
  const attiva = tappe.findIndex(([, fatto]) => !fatto)
  return (
    <ol className="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
      {tappe.map(([nome, fatto], i) => (
        <li key={nome} className="flex items-center gap-2">
          <span className={cn('flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs', fatto ? 'border-ok/50 text-ok' : i === attiva ? 'border-accent text-accent' : 'border-line text-muted')}>
            {fatto ? <Check className="size-3.5" /> : <span className={cn('size-2 rounded-full', i === attiva ? 'animate-pulse bg-accent' : 'bg-line')} />}{nome}</span>
          {i < tappe.length - 1 && <span className="text-muted">›</span>}
        </li>
      ))}
    </ol>
  )
}

function Arrivo({ email, input }: { email: Richiesta; input?: string }) {
  const [aperto, setAperto] = useState<string | null>(null)
  const allegati = useQuery({ queryKey: ['allegati', email.id], queryFn: () => api.allegati(email.id), enabled: email.allegati.length > 0 })
  return (
    <div className="grid gap-3 md:grid-cols-[1fr]">
      <div className="overflow-hidden rounded-xl border border-line bg-bg">
        <div className="flex items-center gap-2 border-b border-line bg-surface2 px-3 py-2 text-xs text-muted"><Mail className="size-3.5" />Email ricevuta</div>
        <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 px-3 pt-3 text-sm">
          <dt className="text-muted">Da</dt><dd className="font-medium">{email.da}</dd>
          <dt className="text-muted">Data</dt><dd>{email.data}</dd>
          <dt className="text-muted">Oggetto</dt><dd className="font-medium">{email.oggetto}</dd>
        </dl>
        <p className="px-3 py-3 text-sm whitespace-pre-wrap">{email.testo}</p>
        {email.allegati.length > 0 && (
          <div className="border-t border-line px-3 py-2">
            <div className="flex flex-wrap gap-2">
              {email.allegati.map((n) => (
                <button key={n} onClick={() => setAperto(aperto === n ? null : n)}
                  className="flex items-center gap-1.5 rounded-lg border border-line px-2.5 py-1 text-xs transition hover:border-accent"><Paperclip className="size-3.5" />{n}<Eye className="size-3.5 text-muted" /></button>
              ))}
            </div>
            {allegati.data?.filter((a) => a.nome === aperto).map((a) => (
              <pre key={a.nome} className="mt-2 max-h-64 overflow-auto rounded-lg border border-line bg-surface p-3 font-mono text-[11px] leading-relaxed text-muted">{a.errore ?? a.testo}</pre>
            ))}
            <p className="mt-1.5 text-[11px] text-muted">Clicca un allegato per vedere il testo che l'agente legge.</p>
          </div>
        )}
      </div>
      {input && <Dettagli titolo="Il testo esatto che riceve l'agente"><pre className="overflow-auto font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-muted">{input}</pre></Dettagli>}
    </div>
  )
}

function Agente({ info }: { info?: { provider: string; istruzioni: string; strumenti: { nome: string; descrizione: string; esterno: boolean }[] } }) {
  if (!info) return <p className="text-sm text-muted">Caricamento…</p>
  const gruppi = [['Può farlo da solo (sola lettura)', info.strumenti.filter((s) => !s.esterno)], ['Serve la tua approvazione (agisce all\'esterno)', info.strumenti.filter((s) => s.esterno)]] as const
  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-muted">Modello in uso: <b className="text-fg">{info.provider}</b> · si cambia senza toccare il resto del sistema.</p>
      <div className="grid gap-3 md:grid-cols-2">
        {gruppi.map(([titolo, lista], i) => (
          <div key={titolo} className={cn('rounded-xl border p-3', i ? 'border-warn/40' : 'border-line')}>
            <div className={cn('mb-2 flex items-center gap-1.5 text-xs font-medium', i ? 'text-warn' : 'text-muted')}>{i ? <ShieldCheck className="size-3.5" /> : <Eye className="size-3.5" />}{titolo}</div>
            <ul className="flex flex-col gap-1.5 text-sm">
              {lista.map((s) => <li key={s.nome}><span className="font-medium">{nomeTool(s.nome)}</span><span className="block text-xs text-muted">{s.descrizione}</span></li>)}
            </ul>
          </div>
        ))}
      </div>
      <Dettagli titolo="Le istruzioni date all'agente"><pre className="overflow-auto font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-muted">{info.istruzioni}</pre></Dettagli>
    </div>
  )
}

function Dettagli({ titolo, children }: { titolo: string; children: ReactNode }) {
  const [aperto, setAperto] = useState(false)
  return (
    <div className="rounded-xl border border-line bg-bg">
      <button onClick={() => setAperto(!aperto)} className="flex w-full items-center justify-between px-3 py-2 text-left text-xs text-muted transition hover:text-fg">
        <span className="flex items-center gap-1.5"><FileText className="size-3.5" />{titolo}</span><ChevronDown className={cn('size-4 transition', aperto && 'rotate-180')} /></button>
      {aperto && <div className="border-t border-line p-3">{children}</div>}
    </div>
  )
}

function FaseCard({ f, n, prima, ultima, esterni }: { f: Fase; n: number; prima: boolean; ultima: boolean; esterni: Set<string> }) {
  const pensiero = f.llm.testo as string
  const titolo = prima ? 'Presa in carico: capisce che richiesta è' : ultima ? 'Conclusione' : 'Ragiona sul prossimo passo'
  return (
    <motion.li initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-line bg-bg p-3">
      <div className="flex items-center justify-between gap-2 text-xs text-muted">
        <span className="flex items-center gap-1.5 font-medium text-accent"><Brain className="size-4" />Passo {n} · {titolo}</span>
        {f.llm.durata_ms != null && <span className="font-mono">{(f.llm.durata_ms / 1000).toFixed(1)} s</span>}
      </div>
      <div className="mt-2">
        <div className="text-[11px] font-medium tracking-wide text-muted uppercase">Cosa pensa e perché</div>
        {pensiero ? <blockquote className="mt-1 border-l-2 border-accent/60 pl-3 text-sm whitespace-pre-wrap">{pensiero}</blockquote>
          : <p className="mt-1 text-sm text-muted italic">Il modello non ha spiegato questo passo.</p>}
      </div>
      {f.operazioni.length > 0 && (
        <div className="mt-3">
          <div className="text-[11px] font-medium tracking-wide text-muted uppercase">Cosa decide di fare</div>
          <ul className="mt-1 flex flex-col gap-2">{f.operazioni.map((o) => <Op key={o.chiamata.id} o={o} esterna={esterni.has(o.chiamata.name) || !!o.attesa} />)}</ul>
        </div>
      )}
    </motion.li>
  )
}

function Op({ o, esterna }: { o: Operazione; esterna: boolean }) {
  const e = o.esito ? leggiEsito(o.chiamata.name, (o.esito.risultato ?? {}) as Record<string, unknown>) : null
  return (
    <li className={cn('rounded-lg border p-2.5', esterna ? 'border-warn/40' : 'border-line')}>
      <div className="flex items-start gap-2 text-sm">
        <Wrench className="mt-0.5 size-4 shrink-0 text-muted" />
        <div className="min-w-0 flex-1">
          <div className="font-medium">{frase(o.chiamata)}</div>
          <span className={cn('mt-0.5 inline-block rounded px-1.5 py-px text-[11px]', esterna ? 'bg-warn/15 text-warn' : 'bg-surface2 text-muted')}>{esterna ? 'Azione esterna · serve approvazione' : 'Sola lettura · automatico'}</span>
        </div>
      </div>
      {o.attesa && !o.decisione && <Riga icona={<Hand className="size-4 text-warn" />}>L'agente si ferma e aspetta la tua decisione.</Riga>}
      {o.modifica && <Riga icona={<Hand className="size-4 text-warn" />}>Hai corretto i dati prima di approvare.</Riga>}
      {o.decisione && (
        <Riga icona={o.decisione.tipo === 'approvato' ? <CheckCircle2 className="size-4 text-ok" /> : <Hand className="size-4 text-bad" />}>
          {o.decisione.tipo === 'approvato' ? 'Hai approvato.' : `Hai rifiutato${o.decisione.motivo ? `: ${o.decisione.motivo as string}` : '.'}`}</Riga>
      )}
      {e && (
        <div className="mt-2 border-t border-line pt-2">
          <div className="text-[11px] font-medium tracking-wide text-muted uppercase">Cosa ottiene</div>
          <p className={cn('mt-0.5 text-sm font-medium', e.ok ? 'text-ok' : 'text-bad')}>{e.sintesi}</p>
          {e.campi.length > 0 && (
            <dl className="mt-1 grid grid-cols-[110px_1fr] gap-x-3 gap-y-0.5 text-sm">
              {e.campi.map((c, i) => <Fragment key={i}><dt className="text-muted">{c.etichetta}</dt><dd>{c.valore}</dd></Fragment>)}
            </dl>
          )}
          {e.note.length > 0 && <ul className="mt-1 list-disc pl-5 text-sm text-bad">{e.note.map((x) => <li key={x}>{x}</li>)}</ul>}
        </div>
      )}
    </li>
  )
}

function Riga({ icona, children }: { icona: ReactNode; children: ReactNode }) {
  return <div className="mt-2 flex items-center gap-2 border-t border-line pt-2 text-sm">{icona}{children}</div>
}

function Esito({ fasi, passi, finale, errore }: { fasi: Fase[]; passi: Passo[]; finale: string; errore: string }) {
  const ops = fasi.flatMap((f) => f.operazioni)
  const fatte = ops.filter((o) => o.decisione?.tipo === 'approvato' && o.esito)
  const rifiutate = ops.filter((o) => o.decisione?.tipo === 'rifiutato')
  const durata = passi.reduce((s, p) => s + (p.durata_ms ?? 0), 0)
  const umane = passi.filter((p) => p.tipo === 'approvato' || p.tipo === 'rifiutato' || p.tipo === 'modificato').length
  const numeri = [['Ragionamenti del modello', fasi.length], ['Operazioni', ops.length], ['Tue decisioni', umane], ['Tempo dell\'agente', `${(durata / 1000).toFixed(1)} s`]]
  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
        {numeri.map(([k, v]) => <div key={k} className="rounded-xl border border-line bg-bg p-3"><div className="text-xl font-semibold">{v}</div><div className="text-xs text-muted">{k}</div></div>)}
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-xl border border-line bg-bg p-3">
          <div className="mb-1 text-xs font-medium tracking-wide text-muted uppercase">Cosa è stato fatto</div>
          {fatte.length ? <ul className="flex flex-col gap-1 text-sm">{fatte.map((o) => <li key={o.chiamata.id} className="flex gap-2"><CheckCircle2 className="mt-0.5 size-4 shrink-0 text-ok" />{frase(o.chiamata)}</li>)}</ul>
            : <p className="text-sm text-muted">Nessuna azione esterna eseguita.</p>}
          {rifiutate.length > 0 && <><div className="mt-3 mb-1 text-xs font-medium tracking-wide text-muted uppercase">Non eseguito (rifiutato da te)</div>
            <ul className="flex flex-col gap-1 text-sm">{rifiutate.map((o) => <li key={o.chiamata.id} className="flex gap-2"><Hand className="mt-0.5 size-4 shrink-0 text-bad" />{frase(o.chiamata)}</li>)}</ul></>}
        </div>
        <div className={cn('rounded-xl border p-3', errore ? 'border-bad/50 bg-bad/10' : 'border-ok/40 bg-ok/10')}>
          <div className="mb-1 text-xs font-medium tracking-wide text-muted uppercase">Il riepilogo dell'agente: cosa ha fatto e perché</div>
          <p className="text-sm whitespace-pre-wrap">{errore || finale}</p>
        </div>
      </div>
    </div>
  )
}
