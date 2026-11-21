import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Play, RotateCcw, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api, type Argomenti, type Dettaglio } from './api'
import { Approvazione } from './components/Approvazione'
import { Grafo } from './components/Grafo'
import { Inbox } from './components/Inbox'
import { Sistemi } from './components/Sistemi'
import { Timeline } from './components/Timeline'
import { usePassi } from './hooks'
import { cn } from './lib'

export default function App() {
  const qc = useQueryClient()
  const [sel, setSel] = useState<string | null>(null)
  const [vista, setVista] = useState<'timeline' | 'grafo'>('timeline')
  const [versione, setVersione] = useState(0) // cambia a ogni azione: ricarica i sistemi
  const passi = usePassi(sel)

  const stato = useQuery({ queryKey: ['stato'], queryFn: api.stato, refetchInterval: 2000 })
  const richieste = useQuery({ queryKey: ['richieste'], queryFn: api.richieste, refetchInterval: 2000 })
  const dettaglio = useQuery({ queryKey: ['dettaglio', sel], queryFn: () => api.dettaglio(sel!), enabled: !!sel, refetchInterval: 1500 })

  useEffect(() => { if (!sel && richieste.data?.length) setSel(richieste.data[0].id) }, [richieste.data, sel])

  const dopoAzione = (d: Dettaglio) => {
    qc.setQueryData(['dettaglio', d.richiesta.id], d)
    qc.invalidateQueries({ queryKey: ['richieste'] }); qc.invalidateQueries({ queryKey: ['stato'] })
    setVersione((v) => v + 1)
  }
  const elabora = useMutation({ mutationFn: () => api.elabora(sel!), onSuccess: dopoAzione })
  const approva = useMutation({ mutationFn: (a: Argomenti) => api.approva(sel!, a), onSuccess: dopoAzione })
  const rifiuta = useMutation({ mutationFn: (m: string) => api.rifiuta(sel!, m), onSuccess: dopoAzione })
  const reset = useMutation({ mutationFn: api.reset, onSuccess: () => { qc.invalidateQueries(); setVersione((v) => v + 1) } })

  const run = dettaglio.data?.run
  const email = dettaglio.data?.richiesta
  const occupato = elabora.isPending || approva.isPending || rifiuta.isPending
  const errore = [elabora, approva, rifiuta].find((m) => m.error)?.error as Error | undefined

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
        <div className="flex items-center gap-2 text-xs">
          <Pill k="Modello" v={stato.data?.provider ?? '…'} />
          <Pill k="Completate" v={stato.data ? `${stato.data.completate}/${stato.data.totale}` : '…'} />
          <Pill k="Tempo medio" v={stato.data?.tempo_medio_ms != null ? `${(stato.data.tempo_medio_ms / 1000).toFixed(1)} s` : '—'} />
          <button onClick={() => reset.mutate()} className="flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-muted transition hover:text-fg">
            <RotateCcw className="size-3.5" />Reset</button>
        </div>
      </header>

      <main className="grid flex-1 gap-4 lg:grid-cols-[320px_1fr_380px]">
        <aside><h2 className="mb-2 text-xs font-medium tracking-wide text-muted uppercase">Richieste in arrivo</h2>
          <Inbox richieste={richieste.data ?? []} selezionata={sel} onSeleziona={setSel} /></aside>

        <section className="min-w-0 rounded-2xl border border-line bg-surface p-4">
          {email && (
            <div className="mb-4 flex items-start justify-between gap-3 border-b border-line pb-4">
              <div className="min-w-0"><div className="text-xs text-muted">{email.da}</div>
                <h2 className="truncate font-semibold">{email.oggetto}</h2></div>
              <button disabled={occupato} onClick={() => elabora.mutate()}
                className="flex shrink-0 items-center gap-1.5 rounded-lg bg-accent px-3.5 py-2 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-50">
                <Play className="size-4" />{elabora.isPending ? 'In corso…' : run ? 'Rielabora' : 'Elabora'}</button>
            </div>
          )}
          <div className="mb-3 flex gap-1 rounded-lg bg-surface2 p-1 text-sm w-fit">
            {(['timeline', 'grafo'] as const).map((v) => (
              <button key={v} onClick={() => setVista(v)} className={cn('rounded-md px-3 py-1 capitalize transition', vista === v ? 'bg-bg text-fg' : 'text-muted')}>{v}</button>
            ))}
          </div>
          {vista === 'timeline' ? <Timeline passi={passi} /> : <Grafo passi={passi} />}
        </section>

        <aside className="flex flex-col gap-4">
          {errore && <div className="rounded-xl border border-bad/50 bg-bad/10 p-3 text-sm text-bad">{errore.message}</div>}
          {run?.stato === 'in_attesa' && run.in_attesa_di && (
            <Approvazione key={run.in_attesa_di.id} chiamata={run.in_attesa_di} occupato={occupato}
              onApprova={(a) => approva.mutate(a)} onRifiuta={(m) => rifiuta.mutate(m)} />
          )}
          {run?.stato === 'completato' && (
            <div className="rounded-2xl border border-ok/40 bg-ok/10 p-4"><div className="text-sm font-semibold text-ok">Completata</div>
              <p className="mt-2 text-sm whitespace-pre-wrap">{run.risposta_finale}</p></div>
          )}
          {run?.stato === 'errore' && <div className="rounded-2xl border border-bad/50 bg-bad/10 p-4 text-sm text-bad">{run.errore}</div>}
          {email && (
            <div className="rounded-2xl border border-line bg-surface p-4"><div className="mb-2 text-xs font-medium tracking-wide text-muted uppercase">Email originale</div>
              <p className="text-sm whitespace-pre-wrap text-muted">{email.testo}</p></div>
          )}
        </aside>
      </main>

      <Sistemi aggiorna={versione} />
    </div>
  )
}

function Pill({ k, v }: { k: string; v: string }) {
  return <span className="rounded-lg border border-line bg-surface px-3 py-1.5"><span className="text-muted">{k} </span><span className="font-medium">{v}</span></span>
}
