import type { ChiamataTool, Passo } from './api'

/** Un'operazione chiesta dal modello, con tutto ciò che le è successo. */
export interface Operazione {
  chiamata: Pick<ChiamataTool, 'id' | 'name' | 'arguments'>
  esito?: Passo        // risultato del tool
  attesa?: Passo       // si è fermata per l'approvazione
  decisione?: Passo    // approvato o rifiutato
  modifica?: Passo     // argomenti corretti dalla persona
}
/** Un giro del ciclo: il modello ragiona, decide, e ne seguono le conseguenze. */
export interface Fase { llm: Passo; operazioni: Operazione[] }

/** Raggruppa i passi grezzi della traccia in fasi leggibili come una storia. */
export function costruisciFasi(passi: Passo[]): Fase[] {
  const fasi: Fase[] = []
  for (const p of passi) {
    if (p.tipo === 'llm') {
      const chiamate = (p.tool_calls as ChiamataTool[] | undefined) ?? []
      fasi.push({ llm: p, operazioni: chiamate.map((chiamata) => ({ chiamata })) })
      continue
    }
    const fase = fasi[fasi.length - 1]
    if (!fase || !['tool', 'in_attesa', 'approvato', 'rifiutato', 'modificato'].includes(p.tipo)) continue
    const nome = p.tool as string
    const op = fase.operazioni.find((o) => o.chiamata.name === nome && !o.esito && !o.decisione)
      ?? fase.operazioni.find((o) => o.chiamata.name === nome && !o.esito)
    if (!op) continue
    if (p.tipo === 'tool') op.esito = p
    else if (p.tipo === 'in_attesa') op.attesa = p
    else if (p.tipo === 'modificato') op.modifica = p
    else op.decisione = p
  }
  return fasi
}
