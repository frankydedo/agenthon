// Traduce i nomi tecnici dei tool in linguaggio da persona dello studio.
// DA ADATTARE al dominio dopo il brief: un tool non elencato qui usa comunque un testo di ripiego.
import type { ChiamataTool, Passo } from './api'

export interface Campo { etichetta: string; valore: string }
export interface Descrizione {
  titolo: string                                   // "Registrare una fattura"
  campi: Campo[]                                   // elenco etichetta/valore
  email?: { a: string; oggetto: string; corpo: string } // anteprima, se l'azione è un'email
  effetto: string                                  // cosa succede se approvi
}

/** Nome leggibile dell'operazione, all'infinito ("Cercare il cliente"). */
export const NOME_TOOL: Record<string, string> = {
  cerca_cliente: 'Cercare il cliente nel gestionale',
  estrai_fattura: 'Leggere la fattura allegata',
  registra_fattura: 'Registrare la fattura in contabilità',
  crea_pratica: 'Aprire una pratica',
  invia_email: 'Inviare un\'email',
}
export const nomeTool = (t: string) => NOME_TOOL[t] ?? t.replaceAll('_', ' ')

const euro = (v: unknown) => (typeof v === 'number' ? v.toLocaleString('it-IT', { style: 'currency', currency: 'EUR' }) : String(v ?? '—'))
const data = (v: unknown) => (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) ? v.split('-').reverse().join('/') : String(v ?? '—'))
const testo = (v: unknown) => (v === undefined || v === null || v === '' ? '—' : String(v))

/** `clienti` serve a trasformare un id numerico nel nome del cliente. */
export function descrivi(c: ChiamataTool, clienti: Record<string, unknown>[]): Descrizione {
  const a = c.arguments
  const cliente = () => {
    const trovato = clienti.find((x) => x.id === a.cliente_id)
    return trovato ? `${trovato.nome ?? ''} (n. ${a.cliente_id})`.trim() : `Cliente n. ${testo(a.cliente_id)}`
  }
  switch (c.name) {
    case 'invia_email':
      return {
        titolo: nomeTool(c.name), campi: [],
        email: { a: testo(a.destinatario), oggetto: testo(a.oggetto), corpo: testo(a.testo) },
        effetto: 'L\'email parte subito dalla casella dello studio.',
      }
    case 'registra_fattura':
      return {
        titolo: nomeTool(c.name), effetto: 'La fattura viene registrata nella contabilità del cliente.',
        campi: [
          { etichetta: 'Cliente', valore: cliente() }, { etichetta: 'Fornitore', valore: testo(a.fornitore) },
          { etichetta: 'P. IVA fornitore', valore: testo(a.partita_iva_fornitore) },
          { etichetta: 'Fattura n.', valore: testo(a.numero) }, { etichetta: 'Data', valore: data(a.data) },
          { etichetta: 'Imponibile', valore: euro(a.imponibile) }, { etichetta: 'IVA', valore: euro(a.iva) },
          { etichetta: 'Totale', valore: euro(a.totale) },
        ],
      }
    case 'crea_pratica':
      return {
        titolo: nomeTool(c.name), effetto: 'Nel gestionale compare una nuova pratica per questo cliente.',
        campi: [
          { etichetta: 'Cliente', valore: cliente() }, { etichetta: 'Tipo di pratica', valore: testo(a.tipo) },
          { etichetta: 'Descrizione', valore: testo(a.descrizione) },
        ],
      }
    default:
      return {
        titolo: nomeTool(c.name), effetto: 'L\'operazione viene eseguita subito.',
        campi: Object.entries(a).map(([k, v]) => ({ etichetta: k.replaceAll('_', ' '), valore: testo(typeof v === 'object' ? JSON.stringify(v) : v) })),
      }
  }
}

/** Una riga di spiegazione per un passo dell'agente, leggibile da chiunque. */
export function spiega(p: Passo): { titolo: string; dettaglio?: string } {
  const tool = (p.tool as string) ?? ''
  switch (p.tipo) {
    case 'inizio': return { titolo: 'Richiesta ricevuta', dettaglio: 'L\'agente legge l\'email e decide cosa fare.' }
    case 'llm': {
      const usi = ((p.tool_calls as { name: string }[]) ?? []).map((c) => nomeTool(c.name))
      return { titolo: usi.length ? `L'agente decide: ${usi.join(', ').toLowerCase()}` : 'L\'agente prepara la risposta finale', dettaglio: (p.testo as string) || undefined }
    }
    case 'tool': {
      const r = (p.risultato ?? {}) as Record<string, unknown>
      const errore = 'errore' in r
      const valore = r.risultato
      const sintesi = errore ? String(r.errore) : Array.isArray(valore) ? `${valore.length} risultat${valore.length === 1 ? 'o' : 'i'}` : 'fatto'
      return { titolo: `${nomeTool(tool)}: ${errore ? 'non riuscito' : 'eseguito'}`, dettaglio: sintesi }
    }
    case 'in_attesa': return { titolo: `Serve il tuo ok: ${nomeTool(tool).toLowerCase()}`, dettaglio: 'L\'agente si è fermato e aspetta la tua decisione.' }
    case 'approvato': return { titolo: `Approvato da te: ${nomeTool(tool).toLowerCase()}` }
    case 'rifiutato': return { titolo: `Rifiutato da te: ${nomeTool(tool).toLowerCase()}`, dettaglio: (p.motivo as string) || undefined }
    case 'modificato': return { titolo: `Hai corretto i dati: ${nomeTool(tool).toLowerCase()}` }
    case 'fine': return { titolo: 'Lavoro completato', dettaglio: (p.testo as string) || undefined }
    case 'errore': return { titolo: 'Qualcosa è andato storto', dettaglio: p.messaggio as string }
  }
}

// --- Per la schermata «Come ragiona l'agente» ---------------------------------------------------

/** Cosa decide di fare l'agente, in una frase. */
export function frase(c: { name: string; arguments: Record<string, unknown> }): string {
  const a = c.arguments
  switch (c.name) {
    case 'cerca_cliente': return `Cerca «${testo(a.testo)}» nell'anagrafica clienti`
    case 'estrai_fattura': return `Legge il file ${testo(a.nome_file)} ed estrae i dati`
    case 'registra_fattura': return `Registra la fattura n. ${testo(a.numero)} di ${testo(a.fornitore)} (${euro(a.totale)})`
    case 'crea_pratica': return `Apre una pratica «${testo(a.tipo)}»`
    case 'invia_email': return `Scrive a ${testo(a.destinatario)}: «${testo(a.oggetto)}»`
    default: return `${nomeTool(c.name)} (${JSON.stringify(a).slice(0, 120)})`
  }
}

export interface Esito { ok: boolean; sintesi: string; campi: Campo[]; note: string[] }

/** Cosa ha ottenuto l'agente da un tool, in linguaggio comprensibile. */
export function leggiEsito(tool: string, r: Record<string, unknown>): Esito {
  if ('errore' in r) {
    const det = Array.isArray(r.dettagli) ? (r.dettagli as { campo: string; problema: string }[]).map((d) => `${d.campo}: ${d.problema}`) : []
    return { ok: false, sintesi: String(r.errore), campi: [], note: det }
  }
  const v = r.risultato
  if (tool === 'cerca_cliente' && Array.isArray(v)) {
    if (!v.length) return { ok: true, sintesi: 'Nessun cliente trovato', campi: [], note: [] }
    return {
      ok: true, sintesi: v.length === 1 ? 'Trovato 1 cliente' : `Trovati ${v.length} clienti`, note: [],
      campi: (v as Record<string, unknown>[]).map((c) => ({ etichetta: `Cliente n. ${testo(c.id)}`, valore: [c.nome, c.email, c.partita_iva].filter(Boolean).join(' · ') })),
    }
  }
  if (tool === 'estrai_fattura' && v && typeof v === 'object') {
    const f = v as { dati?: Record<string, unknown>; controlli_superati?: boolean; avvisi?: string[] }
    const d = f.dati ?? {}
    return {
      ok: !!f.controlli_superati,
      sintesi: f.controlli_superati ? 'Dati estratti, controlli automatici superati' : 'Dati estratti, ma i controlli automatici hanno trovato problemi',
      campi: [
        { etichetta: 'Fattura n.', valore: testo(d.numero) }, { etichetta: 'Data', valore: data(d.data) }, { etichetta: 'Fornitore', valore: testo(d.fornitore) },
        { etichetta: 'P. IVA', valore: testo(d.partita_iva_fornitore) }, { etichetta: 'Imponibile', valore: euro(d.imponibile) },
        { etichetta: 'IVA', valore: euro(d.iva) }, { etichetta: 'Totale', valore: euro(d.totale) },
      ],
      note: f.avvisi ?? [],
    }
  }
  if (['registra_fattura', 'crea_pratica', 'invia_email'].includes(tool)) return { ok: true, sintesi: 'Eseguito con successo', campi: [], note: [] }
  return { ok: true, sintesi: JSON.stringify(v ?? r).slice(0, 240), campi: [], note: [] }
}
