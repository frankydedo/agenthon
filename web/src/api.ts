// Tipi e chiamate verso il backend. Il contratto è in docs/contratto.md (sezione "API HTTP").

export type StatoRun = 'in_corso' | 'in_attesa' | 'completato' | 'errore'
export type Argomenti = Record<string, unknown>

export interface Richiesta {
  id: string; da: string; data: string; oggetto: string; testo: string; allegati: string[]
  stato: StatoRun | null
}
export interface ChiamataTool { id: string; name: string; arguments: Argomenti }
export interface RunPubblico {
  id: string; stato: StatoRun; risposta_finale: string; errore: string; in_attesa_di: ChiamataTool | null
}
export interface Passo {
  ts: string; run_id: string
  tipo: 'inizio' | 'llm' | 'tool' | 'in_attesa' | 'modificato' | 'approvato' | 'rifiutato' | 'fine' | 'errore'
  durata_ms?: number
  [campo: string]: unknown
}
export interface Dettaglio { richiesta: Richiesta; run: RunPubblico | null; passi: Passo[] }
export interface StatoApp {
  provider: string; totale: number; completate: number; da_approvare: string[]; tempo_medio_ms: number | null
}
export interface Sistemi {
  pratiche: Record<string, unknown>[]; fatture: Record<string, unknown>[]; clienti: Record<string, unknown>[]
  email_inviate: { inviata_il: string; destinatario: string; oggetto: string; testo: string }[]
}

async function chiama<T>(percorso: string, metodo = 'GET', corpo?: unknown): Promise<T> {
  const r = await fetch(percorso, {
    method: metodo,
    headers: corpo ? { 'Content-Type': 'application/json' } : undefined,
    body: corpo ? JSON.stringify(corpo) : undefined,
  })
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? `Errore ${r.status}`)
  return r.json()
}

export const api = {
  stato: () => chiama<StatoApp>('/api/stato'),
  richieste: () => chiama<Richiesta[]>('/api/richieste'),
  dettaglio: (id: string) => chiama<Dettaglio>(`/api/richieste/${id}`),
  elabora: (id: string) => chiama<Dettaglio>(`/api/richieste/${id}/elabora`, 'POST'),
  approva: (id: string, argomenti?: Argomenti) => chiama<Dettaglio>(`/api/richieste/${id}/approva`, 'POST', { argomenti: argomenti ?? null }),
  rifiuta: (id: string, motivo: string) => chiama<Dettaglio>(`/api/richieste/${id}/rifiuta`, 'POST', { motivo }),
  sistemi: () => chiama<Sistemi>('/api/sistemi'),
  reset: () => chiama<{ ok: boolean }>('/api/reset', 'POST'),
}
