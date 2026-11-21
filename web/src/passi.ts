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

export const STATO: Record<StatoRun | 'nuovo', { etichetta: string; colore: string }> = {
  nuovo: { etichetta: 'Da elaborare', colore: 'bg-muted' },
  in_corso: { etichetta: 'In corso', colore: 'bg-info' },
  in_attesa: { etichetta: 'Da approvare', colore: 'bg-warn' },
  completato: { etichetta: 'Completata', colore: 'bg-ok' },
  errore: { etichetta: 'Errore', colore: 'bg-bad' },
}
