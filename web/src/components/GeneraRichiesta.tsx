import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, MailPlus } from 'lucide-react'
import { useState } from 'react'
import { api } from '@/api'
import { cn } from '@/lib'

/** Simula l'arrivo di una email. Nessuna richiesta compare da sola: solo con questo pulsante. */
export function GeneraRichiesta({ onGenerata }: { onGenerata: (id: string) => void }) {
  const qc = useQueryClient()
  const [menu, setMenu] = useState(false)
  const sim = useQuery({ queryKey: ['simulazione'], queryFn: api.simulazione })
  const genera = useMutation({
    mutationFn: (id?: string) => api.genera(id),
    onSuccess: (r) => {
      setMenu(false)
      qc.invalidateQueries({ queryKey: ['richieste'] }); qc.invalidateQueries({ queryKey: ['simulazione'] }); qc.invalidateQueries({ queryKey: ['stato'] })
      onGenerata(r.id)
    },
  })
  const resto = sim.data?.disponibili ?? []
  const finite = sim.data && resto.length === 0

  return (
    <div className="rounded-2xl border border-dashed border-accent/50 bg-accent/5 p-3">
      <div className="text-sm font-semibold">Simulatore della casella email</div>
      <p className="mt-1 text-xs leading-relaxed text-muted">
        Qui nessuna richiesta arriva da sola. Premendo <b className="text-fg">Genera richiesta</b> simuli l'arrivo di una nuova email.
        {sim.data && <> {sim.data.sorgente}</>}
      </p>
      <div className="mt-3 flex">
        <button disabled={genera.isPending || !!finite} onClick={() => genera.mutate(undefined)}
          className="flex flex-1 items-center justify-center gap-2 rounded-l-lg bg-accent px-3 py-2 text-sm font-semibold text-bg transition hover:brightness-110 disabled:opacity-40">
          <MailPlus className="size-4" />{finite ? 'Tutte arrivate' : 'Genera richiesta'}</button>
        <button disabled={!!finite} onClick={() => setMenu(!menu)} aria-label="Scegli quale richiesta generare"
          className="rounded-r-lg border-l border-bg/30 bg-accent px-2 text-bg disabled:opacity-40"><ChevronDown className={cn('size-4 transition', menu && 'rotate-180')} /></button>
      </div>
      {sim.data && <p className="mt-1.5 text-[11px] text-muted">{resto.length} di {sim.data.totale} richieste di prova ancora da far arrivare</p>}
      {menu && (
        <ul className="mt-2 max-h-56 overflow-auto rounded-lg border border-line bg-surface text-sm">
          {resto.map((r) => (
            <li key={r.id}><button onClick={() => genera.mutate(r.id)} className="w-full px-3 py-2 text-left transition hover:bg-surface2">
              <span className="block truncate font-medium">{r.oggetto}</span><span className="block truncate text-xs text-muted">{r.da}</span></button></li>
          ))}
        </ul>
      )}
      {genera.error && <p className="mt-2 text-xs text-bad">{(genera.error as Error).message}</p>}
    </div>
  )
}
