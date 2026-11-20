-- Gestionale finto dello "Studio Esempio - Commercialisti Associati".
-- Dati SINTETICI: nomi inventati, email @example.it, partite IVA con codice ufficio 000 (non assegnato).

CREATE TABLE clienti (
    id          INTEGER PRIMARY KEY,
    nome        TEXT NOT NULL,
    tipo        TEXT NOT NULL,          -- ditta individuale, persona fisica, srl, snc, professionista
    partita_iva TEXT,
    email       TEXT,
    referente   TEXT
);

CREATE TABLE pratiche (
    id          INTEGER PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clienti(id),
    tipo        TEXT NOT NULL,
    descrizione TEXT NOT NULL,
    stato       TEXT NOT NULL DEFAULT 'aperta',
    creata_il   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE fatture (
    id                    INTEGER PRIMARY KEY,
    cliente_id            INTEGER NOT NULL REFERENCES clienti(id),
    numero                TEXT NOT NULL,
    data                  TEXT NOT NULL,
    fornitore             TEXT NOT NULL,
    partita_iva_fornitore TEXT NOT NULL,
    imponibile            REAL NOT NULL,
    iva                   REAL NOT NULL,
    totale                REAL NOT NULL,
    registrata_il         TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

INSERT INTO clienti (id, nome, tipo, partita_iva, email, referente) VALUES
    (1, 'Bianchi Impianti di Marco Bianchi', 'ditta individuale', '24681350005', 'marco.bianchi@example.it', 'Marco Bianchi'),
    (2, 'Laura Conti', 'persona fisica', NULL, 'laura.conti@example.it', 'Laura Conti'),
    (3, 'Ferraro Costruzioni Srl', 'srl', '13579240006', 'amministrazione@ferrarocostruzioni.example.it', 'Paolo Ferraro'),
    (4, 'Elena Russo Architetto', 'professionista', '31415920003', 'elena.russo@example.it', 'Elena Russo'),
    (5, 'Panificio Gallo snc', 'snc', '27182810005', 'info@panificiogallo.example.it', 'Giuseppe Gallo');

INSERT INTO pratiche (cliente_id, tipo, descrizione, stato, creata_il) VALUES
    (1, 'contabilità', 'Tenuta contabilità semplificata 2026', 'aperta', '2026-01-10 09:00:00'),
    (3, 'bilancio', 'Bilancio d''esercizio 2025', 'chiusa', '2026-03-02 11:30:00'),
    (5, 'paghe', 'Elaborazione cedolini 2026 (3 dipendenti)', 'aperta', '2026-01-05 10:15:00');

INSERT INTO fatture (cliente_id, numero, data, fornitore, partita_iva_fornitore, imponibile, iva, totale, registrata_il) VALUES
    (1, '2026/0398', '2026-09-30', 'Rossi Forniture Srl', '12345670009', 980.00, 215.60, 1195.60, '2026-10-03 16:20:00');
