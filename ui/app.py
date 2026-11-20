"""Interfaccia della demo: richieste in arrivo, passi dell'agente, approvazioni, effetti sui sistemi.

    streamlit run ui/app.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from core import config, trace  # noqa: E402
from core.agent import carica_run  # noqa: E402
from esempio import connettori  # noqa: E402
from esempio.agente import crea_agente  # noqa: E402

st.set_page_config(page_title="Agente Studio - demo", page_icon="📨", layout="wide")

STATI = {
    None: ("⚪", "da elaborare"),
    "in_corso": ("🔵", "in corso"),
    "in_attesa": ("🟠", "da approvare"),
    "completato": ("🟢", "completata"),
    "errore": ("🔴", "errore"),
}
ICONE = {"inizio": "📥", "llm": "🧠", "tool": "🔧", "in_attesa": "⏸️", "approvato": "✅",
         "rifiutato": "⛔", "modificato": "✏️", "fine": "🏁", "errore": "❌"}


@st.cache_resource
def agente():
    return crea_agente()


def titolo_evento(e: dict) -> str:
    tipo = e["tipo"]
    if tipo == "inizio":
        return f"Richiesta ricevuta (provider: {e.get('provider')})"
    if tipo == "llm":
        strumenti = ", ".join(c["name"] for c in e.get("tool_calls", []))
        testo = e.get("testo") or "Decide il prossimo passo"
        return f"{testo}" + (f"  →  {strumenti}" if strumenti else "")
    if tipo == "tool":
        esito = "errore" if "errore" in e.get("risultato", {}) else "ok"
        return f"Tool {e['tool']}: {esito}"
    if tipo == "in_attesa":
        return f"In attesa di approvazione: {e['tool']}"
    if tipo == "approvato":
        return f"Approvato da una persona: {e['tool']}"
    if tipo == "rifiutato":
        return f"Rifiutato: {e['tool']} ({e.get('motivo') or 'nessun motivo'})"
    if tipo == "modificato":
        return f"Argomenti corretti da una persona: {e['tool']}"
    if tipo == "fine":
        return "Completato"
    if tipo == "errore":
        return f"Errore: {e.get('messaggio')}"
    return tipo


def reset_demo() -> None:
    for percorso in list(config.RUNS_DIR.glob("*.run.json")) + list(config.RUNS_DIR.glob("*.trace.jsonl")):
        percorso.unlink()
    connettori.reset_gestionale()
    connettori.reset_posta()
    st.session_state.clear()


email_list = connettori.elenca_email()
runs = {e["id"]: carica_run(e["id"]) for e in email_list}

# --- Barra laterale: provider, metriche, reset ------------------------------------------------
with st.sidebar:
    st.title("Agente Studio")
    nome_provider = agente().provider.name
    st.caption(f"Provider LLM: **{nome_provider}**")
    if nome_provider == "mock":
        st.info("Modalità mock: risposte registrate, nessun costo. Scenari disponibili per email-001…004.")
    completati = [r for r in runs.values() if r and r.stato == "completato"]
    st.metric("Richieste completate", f"{len(completati)} / {len(email_list)}")
    if completati:
        # Tempo di lavoro dell'agente (modello + tool), escluse le attese per l'approvazione umana.
        tempi = [sum(e.get("durata_ms", 0) for e in trace.leggi(r.id)) for r in completati]
        st.metric("Tempo medio dell'agente", f"{sum(tempi) / len(tempi) / 1000:.1f} s")
    in_attesa = [r.id for r in runs.values() if r and r.stato == "in_attesa"]
    if in_attesa:
        st.warning("Da approvare: " + ", ".join(in_attesa))
    if st.button("Reset demo", key="reset"):
        reset_demo()
        st.rerun()

col_inbox, col_passi, col_azioni = st.columns([1, 1.6, 1.2], gap="medium")

# --- Colonna 1: richieste in arrivo -----------------------------------------------------------
with col_inbox:
    st.subheader("📨 Richieste in arrivo")
    for email in email_list:
        run = runs[email["id"]]
        icona, etichetta = STATI[run.stato if run else None]
        with st.container(border=True):
            st.markdown(f"**{email['oggetto']}**  \n{email['da']}  \n{icona} {etichetta}")
            c1, c2 = st.columns(2)
            if c1.button("Apri", key=f"apri-{email['id']}"):
                st.session_state.sel = email["id"]
            if c2.button("Rielabora" if run else "Elabora", key=f"elabora-{email['id']}",
                         type="secondary" if run else "primary"):
                with st.spinner("L'agente sta lavorando…"):
                    agente().avvia(connettori.formatta_email(email), run_id=email["id"])
                st.session_state.sel = email["id"]
                st.rerun()

sel = st.session_state.get("sel")
run_sel = runs.get(sel) if sel else None

# --- Colonna 2: passi dell'agente (dalla traccia) ---------------------------------------------
with col_passi:
    st.subheader("🧭 Passi dell'agente")
    if not sel:
        st.caption("Apri o elabora una richiesta per vedere cosa fa l'agente, passo per passo.")
    else:
        with st.expander("Email originale"):
            st.text(connettori.formatta_email(connettori.leggi_email(sel)))
        eventi = trace.leggi(sel)
        if not eventi:
            st.caption("Non ancora elaborata.")
        for e in eventi:
            durata = f" · {e['durata_ms']} ms" if "durata_ms" in e else ""
            with st.expander(f"{ICONE.get(e['tipo'], '•')} {titolo_evento(e)}",
                             expanded=e["tipo"] in ("in_attesa", "errore")):
                st.caption(f"{e['ts']}{durata}")
                st.json({k: v for k, v in e.items() if k not in ("ts", "run_id", "tipo", "durata_ms")})

# --- Colonna 3: approvazione umana ------------------------------------------------------------
with col_azioni:
    st.subheader("✋ Approvazione")
    if run_sel and run_sel.stato == "in_attesa":
        chiamata = run_sel.in_attesa_di
        st.markdown(f"L'agente vuole eseguire **{chiamata.name}**. Controlla, correggi se serve, decidi.")
        testo_args = st.text_area("Argomenti (modificabili)", json.dumps(chiamata.arguments, ensure_ascii=False, indent=2),
                                  height=280, key=f"args-{run_sel.id}-{chiamata.id}")
        motivo = st.text_input("Motivo (se rifiuti)", key=f"motivo-{run_sel.id}-{chiamata.id}")
        a, r = st.columns(2)
        if a.button("✅ Approva", type="primary", key=f"approva-{run_sel.id}"):
            try:
                argomenti = json.loads(testo_args)
            except json.JSONDecodeError as errore:
                st.error(f"JSON non valido: {errore}")
            else:
                with st.spinner("Eseguo e proseguo…"):
                    agente().approva(run_sel.id, argomenti)
                st.rerun()
        if r.button("⛔ Rifiuta", key=f"rifiuta-{run_sel.id}"):
            with st.spinner("Proseguo senza eseguire…"):
                agente().rifiuta(run_sel.id, motivo)
            st.rerun()
    elif run_sel and run_sel.stato == "completato":
        st.success(run_sel.risposta_finale)
    elif run_sel and run_sel.stato == "errore":
        st.error(run_sel.errore)
    else:
        st.caption("Nessuna azione in attesa per questa richiesta.")

# --- Sotto: effetti sui sistemi dello studio --------------------------------------------------
st.divider()
st.subheader("🗂️ Sistemi dello studio (simulati)")
t_pratiche, t_fatture, t_posta, t_clienti = st.tabs(["Pratiche", "Fatture registrate", "Email inviate", "Clienti"])
with t_pratiche:
    st.dataframe(connettori.tabella("pratiche"), hide_index=True)
with t_fatture:
    st.dataframe(connettori.tabella("fatture"), hide_index=True)
with t_posta:
    inviate = connettori.email_inviate()
    if not inviate:
        st.caption("Nessuna email inviata.")
    for m in reversed(inviate):
        with st.expander(f"{m['inviata_il']} → {m['destinatario']}: {m['oggetto']}"):
            st.text(m["testo"])
with t_clienti:
    st.dataframe(connettori.tabella("clienti"), hide_index=True)
