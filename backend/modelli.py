"""CONTRATTO CONDIVISO del backend: gli schemi dei dati del Company Brain.

Ogni parte del team (AI, backend, interfaccia) usa questi tipi. **Si cambiano solo dopo averne
parlato** (vedi `solution.md` §6): chi li cambia aggiorna anche i dati finti in `dati/`.

Convenzioni:
- Identificativi stringa leggibili con prefisso: persone `p-01`, progetti `prj-01`, riunioni `riu-001`,
  segmenti `riu-001#s012`, task `task-001`, fatti `fat-001`, proposte `prop-001`, avvisi `avv-001`.
- Campi in italiano, snake_case. Date in ISO (`AAAA-MM-GG`), orari delle riunioni in secondi.
- Tre famiglie di modelli:
    1. **Dati di base**: progetto, persone, riunioni e segmenti.
    2. **Output del modello** (`*Estratto`): ciò che l'LLM restituisce analizzando una riunione.
       NON contiene id di persone risolti né citazioni: quelli li calcola il codice.
    3. **Dati del dominio**: task, fatti, proposte, avvisi, to-do, domande, registro.

Regola d'oro (solution.md §3): permessi, abbinamento delle persone, citazioni, «non lo so»,
approvazioni e dipendenze li decide il CODICE, mai il modello.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# =================================================================================================
# Enumerazioni
# =================================================================================================

class Area(StrEnum):
    """Aree di competenza. Una persona vede un'informazione se ha ALMENO UNA delle sue aree.
    `generale` è visibile a tutti i membri del progetto."""
    SVILUPPO = "sviluppo"
    BUDGET = "budget"
    COMMERCIALE = "commerciale"
    FORNITORI = "fornitori"
    PERSONALE = "personale"
    GENERALE = "generale"


class Sicurezza(StrEnum):
    """Quanto il modello è sicuro. `bassa` genera automaticamente un punto oscuro da chiarire."""
    ALTA = "alta"
    MEDIA = "media"
    BASSA = "bassa"


class FonteRiunione(StrEnum):
    MINUTA = "minuta"              # testo scritto, senza orari
    TRASCRIZIONE = "trascrizione"  # testo con chi parla (eventualmente con orari)
    AUDIO = "audio"                # registrazione trascritta con ElevenLabs (orari e speaker)


class StatoTask(StrEnum):
    """`bloccato` lo calcola il codice dalle dipendenze. Gli altri cambiano solo con una proposta
    approvata dal manager o, per `in_corso`, dalla persona sulla propria to-do."""
    DA_FARE = "da_fare"
    IN_CORSO = "in_corso"
    BLOCCATO = "bloccato"
    FATTO = "fatto"
    ANNULLATO = "annullato"


class Attributo(StrEnum):
    """Lista chiusa degli attributi dei fatti: il codice confronta lo stesso (soggetto, attributo)
    tra riunioni e trova le incongruenze senza il modello. `altro` lo confronta il modello."""
    SCADENZA = "scadenza"
    RESPONSABILE = "responsabile"
    BUDGET = "budget"
    COSTO = "costo"
    STATO = "stato"
    FORNITORE = "fornitore"
    DECISIONE = "decisione"
    REQUISITO = "requisito"
    RISCHIO = "rischio"
    ALTRO = "altro"


class TipoProposta(StrEnum):
    """Modifiche alla lista del progetto o alla memoria: il manager le approva o le rifiuta."""
    NUOVO_TASK = "nuovo_task"
    AGGIORNA_TASK = "aggiorna_task"   # cambio di scadenza, assegnatario, stato, descrizione
    CHIUDI_TASK = "chiudi_task"       # es. «ho fatto questo» nella riunione di fine giornata
    NUOVO_FATTO = "nuovo_fatto"       # entra nella memoria del progetto


class StatoProposta(StrEnum):
    IN_ATTESA = "in_attesa"
    APPROVATA = "approvata"
    RIFIUTATA = "rifiutata"


class TipoAvviso(StrEnum):
    """Avvisi: non si approvano, si vedono e si risolvono (es. scegliendo l'assegnatario giusto)."""
    INCONGRUENZA = "incongruenza"           # due riunioni dicono cose diverse
    PUNTO_OSCURO = "punto_oscuro"           # task o assegnatario non chiaro
    SCONOSCIUTO = "sconosciuto"             # persona o contesto mai visti
    DIPENDENZA_A_RISCHIO = "dipendenza_a_rischio"
    EVENTO_ESTERNO = "evento_esterno"       # errore nel codice, problema di un collega
    BRIEF = "brief"                         # il Brain parla per primo (es. brief del mattino)


class StatoAvviso(StrEnum):
    APERTO = "aperto"
    RISOLTO = "risolto"


class TipoSconosciuto(StrEnum):
    PERSONA = "persona"
    CONTESTO = "contesto"   # sistema, cliente, fornitore, progetto, sigla mai visti


class StatoTodo(StrEnum):
    PROPOSTA = "proposta"     # preparata dal Brain al mattino
    ACCETTATA = "accettata"   # accettata dalla persona (che può poi modificarla)


class EsitoRisposta(StrEnum):
    RISPOSTA = "risposta"
    NON_LO_SO = "non_lo_so"              # il dato non c'è (deciso dal codice se la ricerca è vuota)
    NON_AUTORIZZATO = "non_autorizzato"  # il dato c'è ma non rientra nelle competenze di chi chiede


# =================================================================================================
# 1. Dati di base
# =================================================================================================

class Persona(BaseModel):
    id: str = Field(examples=["p-01"])
    nome: str
    cognome: str
    email: str
    ruolo: str = Field(description="Descrizione libera, es. 'sviluppatore senior', 'responsabile acquisti'")
    reparto: str
    competenze: list[Area] = Field(description="Aree visibili. Es. senior dev: [sviluppo, budget]")
    alias: list[str] = Field(default_factory=list, description="Come viene chiamata nelle riunioni: 'Marco', 'Rossi', 'il capo'")


class Progetto(BaseModel):
    id: str = Field(examples=["prj-01"])
    nome: str
    cliente: str
    descrizione: str
    scadenza: date
    manager_id: str = Field(description="Il manager DEL PROGETTO: approva le proposte e vede tutto il progetto")
    membri: list[str] = Field(description="Id delle persone coinvolte (anche di reparti diversi), manager compreso")


class Segmento(BaseModel):
    """Un turno di parola: l'unità che si cita.

    Da audio (ElevenLabs Speech-to-Text): la risposta contiene `words` con `text`, `type`
    (word | spacing | audio_event), `start`/`end` in secondi e `speaker_id` ('speaker_0', ...).
    Il codice raggruppa le parole consecutive dello stesso `speaker_id` in un segmento.
    Da minuta di testo: un segmento per riga/intervento, senza orari.
    """
    id: str = Field(examples=["riu-001#s012"])
    riunione_id: str
    posizione: int = Field(description="Ordine nella riunione, da 1")
    speaker: str | None = Field(default=None, description="Etichetta grezza: 'speaker_0' da ElevenLabs o il nome scritto nella minuta")
    persona_id: str | None = Field(default=None, description="Persona abbinata dal codice (o confermata dal manager); None se non nota")
    inizio: float | None = Field(default=None, description="Secondi dall'inizio; solo se c'è l'audio")
    fine: float | None = None
    testo: str


class Riunione(BaseModel):
    id: str = Field(examples=["riu-001"])
    progetto_id: str
    titolo: str
    data: date
    fonte: FonteRiunione
    partecipanti: list[str] = Field(description="Id delle persone presenti")
    aree_predefinite: list[Area] = Field(default_factory=lambda: [Area.GENERALE],
                                         description="Aree suggerite per ciò che emerge (es. riunione sui costi -> [budget])")
    file_audio: str | None = None
    segmenti: list[Segmento] = Field(default_factory=list)


# =================================================================================================
# 2. Output del modello (analisi di una riunione)
#    Il modello riceve: i segmenti (con id), i membri del progetto, i task aperti (con id).
#    Restituisce SOLO riferimenti a segmenti/task che ha ricevuto; il codice lo verifica.
# =================================================================================================

class TaskEstratto(BaseModel):
    descrizione: str
    assegnatario_detto: str | None = Field(description="Come è stato nominato ('Marco', 'il reparto acquisti'); None se nessuno")
    scadenza: date | None = None
    scadenza_detta: str | None = Field(default=None, description="Il testo originale, es. 'entro fine mese'")
    aree: list[Area] = Field(description="Aree proposte dal modello; il manager le conferma")
    dipende_da: list[str] = Field(default_factory=list, description="Id di task esistenti o descrizioni di task di questa riunione")
    segmenti: list[str] = Field(description="Id dei segmenti da cui nasce (min. 1)", min_length=1)
    sicurezza: Sicurezza


class AggiornamentoEstratto(BaseModel):
    """Una novità su un task già esistente: fatto, cambio scadenza, cambio assegnatario..."""
    task_id: str = Field(description="Id di un task aperto ricevuto in input")
    nuovo_stato: StatoTask | None = None
    nuova_scadenza: date | None = None
    nuovo_assegnatario_detto: str | None = None
    nota: str | None = None
    segmenti: list[str] = Field(min_length=1)
    sicurezza: Sicurezza


class FattoEstratto(BaseModel):
    soggetto: str = Field(description="Di cosa si parla, in forma breve e stabile: 'rilascio v2', 'fornitore motori'")
    attributo: Attributo
    valore: str
    aree: list[Area]
    segmenti: list[str] = Field(min_length=1)
    sicurezza: Sicurezza


class PuntoOscuroEstratto(BaseModel):
    cosa: str = Field(description="Cosa non è chiaro, es. 'chi aggiorna il preventivo'")
    perche: str = Field(description="Es. 'nominato solo Marco, ma nel progetto ci sono due Marco'")
    segmenti: list[str] = Field(min_length=1)


class SconosciutoEstratto(BaseModel):
    nome: str
    tipo: TipoSconosciuto
    segmenti: list[str] = Field(min_length=1)


class EstrazioneRiunione(BaseModel):
    """Tutto ciò che il modello estrae da una riunione (o da un blocco di essa)."""
    task: list[TaskEstratto] = Field(default_factory=list)
    aggiornamenti: list[AggiornamentoEstratto] = Field(default_factory=list)
    fatti: list[FattoEstratto] = Field(default_factory=list)
    punti_oscuri: list[PuntoOscuroEstratto] = Field(default_factory=list)
    sconosciuti: list[SconosciutoEstratto] = Field(default_factory=list)


# =================================================================================================
# 3. Dati del dominio
# =================================================================================================

class Citazione(BaseModel):
    """Generata dal CODICE a partire da un segmento: mai scritta dal modello."""
    riunione_id: str
    riunione_titolo: str
    data: date
    segmento_id: str
    persona_id: str | None = None
    inizio: float | None = None
    testo: str = Field(description="La frase esatta del segmento")


class Task(BaseModel):
    id: str = Field(examples=["task-001"])
    progetto_id: str
    descrizione: str
    assegnatario_id: str | None = None
    scadenza: date | None = None
    stato: StatoTask = StatoTask.DA_FARE
    aree: list[Area]
    dipende_da: list[str] = Field(default_factory=list, description="Id di altri task")
    citazioni: list[Citazione] = Field(default_factory=list)
    creato_il: datetime
    aggiornato_il: datetime


class Fatto(BaseModel):
    """Una voce della memoria del progetto. Esiste solo dopo che una proposta è stata approvata."""
    id: str = Field(examples=["fat-001"])
    progetto_id: str
    soggetto: str
    attributo: Attributo
    valore: str
    aree: list[Area]
    citazioni: list[Citazione]
    approvato_da: str
    approvato_il: datetime


class Proposta(BaseModel):
    """Una modifica proposta dal Brain. Il manager la approva o la rifiuta, voce per voce,
    e può correggere le aree prima di approvare."""
    id: str = Field(examples=["prop-001"])
    progetto_id: str
    riunione_id: str | None = None
    tipo: TipoProposta
    task_id: str | None = Field(default=None, description="Per aggiorna_task e chiudi_task")
    modifiche: dict[str, Any] = Field(default_factory=dict, description="Campo -> nuovo valore, per aggiorna_task")
    bozza_task: Task | None = Field(default=None, description="Per nuovo_task (assegnatario già risolto dal codice, se possibile)")
    bozza_fatto: Fatto | None = Field(default=None, description="Per nuovo_fatto (approvato_da/il riempiti all'approvazione)")
    aree: list[Area]
    sicurezza: Sicurezza
    citazioni: list[Citazione] = Field(min_length=1)
    stato: StatoProposta = StatoProposta.IN_ATTESA
    motivo_rifiuto: str | None = None
    deciso_da: str | None = None
    deciso_il: datetime | None = None
    creata_il: datetime


class Avviso(BaseModel):
    """Il Brain che parla per primo: incongruenze, punti oscuri, sconosciuti, rischi, brief."""
    id: str = Field(examples=["avv-001"])
    progetto_id: str
    riunione_id: str | None = None
    tipo: TipoAvviso
    destinatari: list[str] = Field(description="Id delle persone che devono vederlo (di solito il manager)")
    titolo: str
    testo: str
    aree: list[Area]
    citazioni: list[Citazione] = Field(default_factory=list, description="Per un'incongruenza: le due frasi in conflitto")
    stato: StatoAvviso = StatoAvviso.APERTO
    risoluzione: str | None = None
    risolto_da: str | None = None
    creato_il: datetime


class VoceTodo(BaseModel):
    """Solo task del progetto (decisione del team: niente voci personali)."""
    task_id: str
    ordine: int
    motivo: str | None = Field(default=None, description="Perché oggi, es. 'scade domani', 'sblocca il task di Anna'")


class TodoGiornaliera(BaseModel):
    id: str = Field(examples=["todo-p-03-2026-11-21"])
    persona_id: str
    progetto_id: str
    data: date
    voci: list[VoceTodo]
    stato: StatoTodo = StatoTodo.PROPOSTA
    accettata_il: datetime | None = None


class Domanda(BaseModel):
    persona_id: str = Field(description="Arriva dalla sessione, MAI dal modello")
    progetto_id: str
    testo: str


class Risposta(BaseModel):
    esito: EsitoRisposta
    testo: str
    citazioni: list[Citazione] = Field(default_factory=list, description="Obbligatorie se esito = risposta")


class EventoEsterno(BaseModel):
    """Iniettato dal simulatore in demo (es. errore nel codice, collega malato)."""
    progetto_id: str
    tipo: str = Field(examples=["errore_codice", "problema_collega"])
    descrizione: str
    aree: list[Area]
    task_coinvolti: list[str] = Field(default_factory=list)


class VoceRegistro(BaseModel):
    """Registro di tutto: chi ha fatto cosa, su quale input, chi ha approvato."""
    ts: datetime
    attore: str = Field(description="Id persona oppure 'brain'")
    azione: str = Field(examples=["riunione_caricata", "proposta_approvata", "domanda", "avviso_creato"])
    oggetto_id: str | None = None
    dettaglio: dict[str, Any] = Field(default_factory=dict)


# =================================================================================================
# Regola dei permessi (deterministica, condivisa da tutti)
# =================================================================================================

def puo_vedere(persona: Persona, progetto: Progetto, aree: list[Area]) -> bool:
    """True se la persona può vedere un'informazione con queste aree, in questo progetto.

    - deve essere membro del progetto;
    - il manager del progetto vede tutto;
    - `generale` è visibile a tutti i membri;
    - altrimenti basta ALMENO UNA area in comune con le competenze della persona.
    """
    if persona.id not in progetto.membri:
        return False
    if persona.id == progetto.manager_id or Area.GENERALE in aree:
        return True
    return bool(set(aree) & set(persona.competenze))
