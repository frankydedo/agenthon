import { Brain, CheckCheck, CircleAlert, Flag, Hand, Inbox, PauseCircle, Pencil, Wrench, type LucideIcon } from 'lucide-react'
import type { Passo, StatoRun } from './api'

export const ICONE: Record<Passo['tipo'], LucideIcon> = {
  inizio: Inbox, llm: Brain, tool: Wrench, in_attesa: PauseCircle, approvato: CheckCheck,
  rifiutato: Hand, modificato: Pencil, fine: Flag, errore: CircleAlert,
}
/** Colore (token CSS) di ogni tipo di passo. */
export const COLORE: Record<Passo['tipo'], string> = {
  inizio: 'text-info', llm: 'text-accent', tool: 'text-fg', in_attesa: 'text-warn', approvato: 'text-ok',
  rifiutato: 'text-bad', modificato: 'text-warn', fine: 'text-ok', errore: 'text-bad',
}

export function titolo(p: Passo): string {
  const tool = p.tool as string
  switch (p.tipo) {
    case 'inizio': return 'Richiesta ricevuta'
    case 'llm': {
      const usi = ((p.tool_calls as { name: string }[]) ?? []).map((c) => c.name).join(', ')
      return (p.testo as string) || (usi ? `Decide di usare ${usi}` : 'Ragiona sul prossimo passo')
    }
    case 'tool': return `${tool}: ${'errore' in ((p.risultato as object) ?? {}) ? 'errore' : 'ok'}`
    case 'in_attesa': return `Chiede il permesso: ${tool}`
    case 'approvato': return `Approvato da una persona: ${tool}`
    case 'rifiutato': return `Rifiutato: ${tool}`
    case 'modificato': return `Argomenti corretti da una persona: ${tool}`
    case 'fine': return 'Completato'
    case 'errore': return `Errore: ${p.messaggio as string}`
  }
}

export const STATO: Record<StatoRun | 'nuovo', { etichetta: string; colore: string }> = {
  nuovo: { etichetta: 'Da elaborare', colore: 'bg-muted' },
  in_corso: { etichetta: 'In corso', colore: 'bg-info' },
  in_attesa: { etichetta: 'Da approvare', colore: 'bg-warn' },
  completato: { etichetta: 'Completata', colore: 'bg-ok' },
  errore: { etichetta: 'Errore', colore: 'bg-bad' },
}
