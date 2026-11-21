import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Play, RotateCcw, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { api, type Argomenti, type Dettaglio } from './api'
import { Approvazione } from './components/Approvazione'
import { GeneraRichiesta } from './components/GeneraRichiesta'
import { Grafo } from './components/Grafo'
import { Ragionamento } from './components/Ragionamento'
import { Inbox } from './components/Inbox'
import { Sistemi } from './components/Sistemi'
import { Timeline } from './components/Timeline'
import { usePassi } from './hooks'
import { cn } from './lib'
import { STATO } from './passi'

export default function App() {
  const qc = useQueryClient()
  const [sel, setSel] = useState<string | null>(null)
  const [vista, setVista] = useState<'timeline' | 'grafo'>('timeline')
  const [schermata, setSchermata] = useState<'operativa' | 'ragionamento'>(() => (location.hash === '#ragionamento' ? 'ragionamento' : 'operativa'))
  const vai = (v: 'operativa' | 'ragionamento') => { setSchermata(v); history.replaceState(null, '', v === 'ragionamento' ? '#ragionamento' : location.pathname) }
  const [versione, setVersione] = useState(0) // cambia a ogni azione: ricarica i sistemi

  const stato = useQuery({ queryKey: ['stato'], queryFn: api.stato, refetchInterval: 2000 })
  const richieste = useQuery({ queryKey: ['richieste'], queryFn: api.richieste, refetchInterval: 2000 })
  const esiste = !!sel && !!richieste.data?.some((r) => r.id === sel)
  const idAttivo = esiste ? sel : null
  const passi = usePassi(idAttivo)
  const dettaglio = useQuery({ queryKey: ['dettaglio', idAttivo], queryFn: () => api.dettaglio(idAttivo!), enabled: !!idAttivo, refetchInterval: 1500 })
  const sistemi = useQuery({ queryKey: ['sistemi', versione], queryFn: api.sistemi })

  const dopoAzione = (d: Dettaglio) => {
    qc.setQueryData(['dettaglio', d.richiesta.id], d)
    qc.invalidateQueries({ queryKey: ['richieste'] }); qc.invalidateQueries({ queryKey: ['stato'] })
    setVersione((v) => v + 1)
  }
  const elabora = useMutation({ mutationFn: () => api.elabora(idAttivo!), onSuccess: dopoAzione })
  const approva = useMutation({ mutationFn: (a: Argomenti) => api.approva(idAttivo!, a), onSuccess: dopoAzione })
  const rifiuta = useMutation({ mutationFn: (m: string) => api.rifiuta(idAttivo!, m), onSuccess: dopoAzione })
  const reset = useMutation({ mutationFn: api.reset, onSuccess: () => { setSel(null); qc.invalidateQueries(); setVersione((v) => v + 1) } })

  const run = dettaglio.data?.run
  const email = dettaglio.data?.richiesta
  const occupato = elabora.isPending || approva.isPending || rifiuta.isPending
  const errore = [elabora, approva, rifiuta].find((m) => m.error)?.error as Error | undefined
  // Perché l'agente chiede l'azione: l'ultimo ragionamento del modello prima della pausa.
  const motivazione = [...passi].reverse().find((p) => p.tipo === 'llm' && p.testo)?.testo as string | undefined
  const badge = STATO[run?.stato ?? 'nuovo']

  if (richieste.isError)
    return <div className="grid h-full place-items-center p-8 text-center text-sm text-muted">
      Backend non raggiungibile. Avvia: <code className="ml-2 font-mono text-fg">uvicorn api.main:app --port 8000</code></div>

  return (
    <div className="mx-auto flex min-h-full max-w-[1500px] flex-col gap-4 p-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-xl bg-accent/15 text-accent"><Sparkles className="size-5" /></div>
          <div><h1 className="text-lg font-semibold leading-none">Agente Studio</h1>
            <p className="mt-1 text-xs text-muted">Ogni passo visibile. Ogni azione approvata da te.</p></div>
        </div>
        <nav className="flex gap-1 rounded-xl bg-surface2 p-1 text-sm">
          {([['operativa', 'Operatività'], ['ragionamento', 'Come ragiona l\'agente']] as const).map(([k, nome]) => (
            <button key={k} onClick={() => vai(k)} className={cn('rounded-lg px-3.5 py-1.5 transition', schermata === k ? 'bg-bg font-medium text-fg shadow-sm' : 'text-muted hover:text-fg')}>{nome}</button>
          ))}
        </nav>
        <div className="flex items-center gap-2 text-xs">
          <Pill k="Modello" v={stato.data?.provider ?? '…'} />
          <Pill k="Completate" v={stato.data ? `${stato.data.completate}/${stato.data.totale}` : '…'} />
          <Pill k="Tempo medio" v={stato.data?.tempo_medio_ms != null ? `${(stato.data.tempo_medio_ms / 1000).toFixed(1)} s` : '—'} />
          <button onClick={() => reset.mutate()} className="flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-muted transition hover:text-fg">
            <RotateCcw className="size-3.5" />Reset</button>
        </div>
      </header>

      {schermata === 'ragionamento' ? (
        <Ragionamento richieste={richieste.data ?? []} selezionata={idAttivo} onSeleziona={setSel} dettaglio={dettaglio.data} passi={passi}
          clienti={sistemi.data?.clienti ?? []} occupato={occupato} inCorso={elabora.isPending} errore={errore?.message}
          onElabora={() => elabora.mutate()} onApprova={(a) => approva.mutate(a)} onRifiuta={(m) => rifiuta.mutate(m)} />
      ) : (<>
      <main className="grid flex-1 gap-4 lg:grid-cols-[320px_1fr_400px]">
        <aside className="flex flex-col gap-3">
          <GeneraRichiesta onGenerata={setSel} />
          <h2 className="text-xs font-medium tracking-wide text-muted uppercase">Richieste in arrivo</h2>
          <Inbox richieste={richieste.data ?? []} selezionata={idAttivo} onSeleziona={setSel} />
        </aside>

        <section className="min-w-0 rounded-2xl border border-line bg-surface p-4">
          {!email ? <Guida /> : (
            <>
              <div className="mb-4 flex items-start justify-between gap-3 border-b border-line pb-4">
                <div className="min-w-0">
                  <div className="text-xs text-muted">{email.da}</div>
                  <h2 className="truncate font-semibold">{email.oggetto}</h2>
                  <span className="mt-1.5 inline-flex items-center gap-1.5 rounded-full border border-line px-2.5 py-0.5 text-xs">
                    <span className={cn('size-2 rounded-full', badge.colore, run?.stato === 'in_attesa' && 'animate-pulse')} />{badge.etichetta}</span>
                </div>
                <button disabled={occupato} onClick={() => elabora.mutate()}
                  className="flex shrink-0 items-center gap-1.5 rounded-lg bg-accent px-3.5 py-2 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-50">
                  <Play className="size-4" />{elabora.isPending ? 'In corso…' : run ? 'Rielabora' : 'Avvia l\'agente'}</button>
              </div>
              <div className="mb-3 flex items-center justify-between gap-2">
                <h3 className="text-sm font-semibold">Flusso delle operazioni <span className="font-normal text-muted">· il più recente in alto</span></h3>
                <div className="flex w-fit gap-1 rounded-lg bg-surface2 p-1 text-sm">
                  {(['timeline', 'grafo'] as const).map((v) => (
                    <button key={v} onClick={() => setVista(v)} className={cn('rounded-md px-3 py-1 capitalize transition', vista === v ? 'bg-bg text-fg' : 'text-muted')}>{v}</button>
                  ))}
                </div>
              </div>
              {vista === 'timeline' ? <Timeline passi={passi} /> : <Grafo passi={passi} />}
            </>
          )}
        </section>

        <aside className="flex flex-col gap-4">
          {errore && <div className="rounded-xl border border-bad/50 bg-bad/10 p-3 text-sm text-bad">{errore.message}</div>}
          {run?.stato === 'in_attesa' && run.in_attesa_di && (
            <Approvazione key={run.in_attesa_di.id} chiamata={run.in_attesa_di} motivazione={motivazione}
              clienti={sistemi.data?.clienti ?? []} occupato={occupato}
              onApprova={(a) => approva.mutate(a)} onRifiuta={(m) => rifiuta.mutate(m)} />
          )}
          {run?.stato === 'completato' && (
            <div className="rounded-2xl border border-ok/40 bg-ok/10 p-4"><div className="text-sm font-semibold text-ok">Lavoro completato</div>
              <p className="mt-2 text-sm whitespace-pre-wrap">{run.risposta_finale}</p></div>
          )}
          {run?.stato === 'errore' && <div className="rounded-2xl border border-bad/50 bg-bad/10 p-4 text-sm text-bad">{run.errore}</div>}
          {email && (
            <div className="rounded-2xl border border-line bg-surface p-4"><div className="mb-2 text-xs font-medium tracking-wide text-muted uppercase">Email ricevuta dal cliente</div>
              <p className="text-sm whitespace-pre-wrap text-muted">{email.testo}</p>
              {email.allegati.length > 0 && <p className="mt-2 text-xs text-muted">Allegati: {email.allegati.join(', ')}</p>}</div>
          )}
        </aside>
      </main>

      <Sistemi aggiorna={versione} />
      </>)}
    </div>
  )
}

function Guida() {
  const passi = [
    ['1', 'Genera una richiesta', 'A sinistra: simula l\'arrivo di una email di un cliente nella casella dello studio.'],
    ['2', 'Avvia l\'agente', 'Legge l\'email, consulta i dati e prepara le azioni. Vedi ogni passo qui, il più recente in alto.'],
    ['3', 'Approva o rifiuta', 'Prima di ogni azione verso l\'esterno (registrare, inviare) l\'agente si ferma e aspetta il tuo ok.'],
  ]
  return (
    <div className="mx-auto max-w-md py-10">
      <h2 className="text-lg font-semibold">Come funziona</h2>
      <ol className="mt-4 flex flex-col gap-3">
        {passi.map(([n, t, d]) => (
          <li key={n} className="flex gap-3 rounded-xl border border-line bg-bg p-3">
            <span className="grid size-7 shrink-0 place-items-center rounded-full bg-accent/15 text-sm font-semibold text-accent">{n}</span>
            <span><span className="block text-sm font-medium">{t}</span><span className="text-sm text-muted">{d}</span></span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function Pill({ k, v }: { k: string; v: string }) {
  return <span className="rounded-lg border border-line bg-surface px-3 py-1.5"><span className="text-muted">{k} </span><span className="font-medium">{v}</span></span>
}
