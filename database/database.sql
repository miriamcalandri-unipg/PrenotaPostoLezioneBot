DROP DATABASE IF EXISTS DatabaseBot;
CREATE DATABASE IF NOT EXISTS DatabaseBot;
USE DatabaseBot;

DROP TABLE IF EXISTS CorsiDiLaurea;
CREATE TABLE IF NOT EXISTS CorsiDiLaurea (
  nome VARCHAR(20) NOT NULL,
  PRIMARY KEY(nome)
);

DROP TABLE IF EXISTS Professori;
CREATE TABLE IF NOT EXISTS Professori (
  nome VARCHAR(20) NOT NULL,
  cognome VARCHAR(20) NOT NULL, 
  PRIMARY KEY (nome, cognome)
);

DROP TABLE IF EXISTS Materie;
CREATE TABLE IF NOT EXISTS Materie (
  nome VARCHAR(100) NOT NULL,
  anno_di_corso INT NOT NULL,
  PRIMARY KEY(nome)
);

DROP TABLE IF EXISTS Aule;
CREATE TABLE IF NOT EXISTS Aule (
  nome VARCHAR(2) NOT NULL,
  posti_totali INT NOT NULL,
  PRIMARY KEY(nome)
); 

DROP TABLE IF EXISTS Utenti;
CREATE TABLE IF NOT EXISTS Utenti (
  email VARCHAR(50) NOT NULL,
  nome VARCHAR(20) NOT NULL,
  cognome VARCHAR(20) NOT NULL,
  anno_di_corso INT NOT NULL,
  nome_corso VARCHAR(20) NOT NULL,
  CONSTRAINT corso_utente FOREIGN KEY(nome_corso) REFERENCES CorsiDiLaurea(nome) ON UPDATE CASCADE ON DELETE CASCADE
  PRIMARY KEY (email)
);

DROP TABLE IF EXISTS Insegnamenti;
CREATE TABLE IF NOT EXISTS Insegnamenti (
  nome_corso VARCHAR(20) NOT NULL,
  nome_materia VARCHAR(100) NOT NULL,
  CONSTRAINT corso_insegnamento FOREIGN KEY (nome_corso) REFERENCES CorsiDiLaurea(nome) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT materia_insegnamento FOREIGN KEY (nome_materia) REFERENCES Materie(nome) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (nome_corso, nome_materia)
);

DROP TABLE IF EXISTS Lezioni;
CREATE TABLE IF NOT EXISTS Lezioni (
  id_lezione INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  ora TIME NOT NULL,
  descrizione VARCHAR(500) NOT NULL,
  posti_disponibili INT,
  nome_materia VARCHAR(100) NOT NULL,
  nome_aula VARCHAR(2) NOT NULL,
  nome_professore VARCHAR(20),
  cognome_professore VARCHAR(20),
  CONSTRAINT materia_lezione FOREIGN KEY (nome_materia) REFERENCES Materie(nome) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT aula_lezione FOREIGN KEY (nome_aula) REFERENCES Aule(nome) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT professore_lezione FOREIGN KEY (nome_professore, cognome_professore) REFERENCES Professori(nome, cognome) ON UPDATE CASCADE ON DELETE CASCADE
);

DROP TABLE IF EXISTS Prenotazioni;
CREATE TABLE IF NOT EXISTS Prenotazioni (
  id_prenotazione INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  ora TIME NOT NULL,
  id_lezione INT NOT NULL,
  email_utente INT NOT NULL,
  CONSTRAINT lezione_prenotazione FOREIGN KEY (id_lezione) REFERENCES Lezioni(id_lezione) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT utente_prenotazione FOREIGN KEY (email_utente) REFERENCES Utenti(email) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO CorsiDiLaurea (nome) VALUES 
("Informatica"), 
("Matematica"), 
("Medicina"), 
("Giurisprudenza"), 
("Filosofia"), 
("Fisica"),
("Economia"); 

INSERT INTO Professori (nome, cognome) VALUES
("Francesco", "Santini"),
("Stefano", "Marcugini"),
("Maria Cristina", "Pinotti"),
("Osvaldo", "Gervasi"),
("Arturo", "Carpi"),
("Gino", "Tosti"),
("Raffaella", "Gentilini"),
("Daniele", "Bartoli"),
("Paola", "Rubbioni"),
("Gianfranco", "Baldini"),
("Stefania", "Stefanelli"),
("Luca", "Franchi"),
("Sonia", "Tulli"),
("Maria", "Graziosi"),
("Roberta", "Cruschi"),
("Lorenzo", "Capoccioni");

INSERT INTO Materie (nome, anno_di_corso) VALUES
("Programmazione Procedurale", 1),
("Programmazione ad Oggetti", 1),
("Algoritmi e Strutture Dati", 2),
("Sistemi Operativi", 2),
("Sistemi di realtà virtuale", 3),
("Basi di dati", 3),
("Analisi I", 1),
("Geometria I", 1),
("Analisi II", 2),
("Geometria II", 2),
("Analisi III", 3),
("Geometria III", 3),
("Chimica e Biochimica I", 1),
("Istologia ed embriologia umana", 1),
("Microbiologia", 2),
("Fisiologia", 2),
("Medicina di laboratorio", 3),
("Patologia Sistemica", 3),
("Filosofia del Diritto", 1),
("Economia Politica", 1),
("Diritto Internazionale", 2),
("Diritto del Lavoro", 2),
("Diritto Civile", 3),
("Diritto Penale", 3),
("Storia Moderna", 1),
("Paradigmi di razionalità pratica", 1),
("Antropologia culturale", 2),
("Entropsichiatria", 2),
("Filosofia Morale", 3),
("Culture e religioni del mondo antico", 3),
("Fisica I", 1),
("Laboratorio I", 1),
("Fisica II", 2),
("Laboratorio II", 2),
("Fisica III", 3),
("Laboratorio III", 3),
("Economia Aziendale", 1),
("Matematica Generale", 1),
("Diritto Commerciale", 2),
("Economia Industriale", 2),
("Diritto Tributario", 3),
("Programmazione e Controllo", 3);

INSERT INTO Insegnamenti (nome_corso, nome_materia) VALUES
("Informatica", "Programmazione Procedurale"),
("Informatica", "Programmazione ad Oggetti"),
("Informatica", "Algoritmi e Strutture Dati"),
("Informatica", "Sistemi Operativi"),
("Informatica", "Sistemi di realtà virtuale"),
("Informatica", "Basi di dati"),
("Matematica", "Analisi I"),
("Matematica", "Geometria I"),
("Matematica", "Analisi II"),
("Matematica", "Geometria II"),
("Matematica", "Analisi III"),
("Matematica", "Geometria III"),
("Medicina", "Chimica e Biochimica I"),
("Medicina", "Istologia ed embriologia umana"),
("Medicina", "Microbiologia"),
("Medicina", "Fisiologia"),
("Medicina", "Medicina di laboratorio"),
("Medicina", "Patologia Sistemica"),
("Giurisprudenza", "Filosofia del Diritto"),
("Giurisprudenza", "Economia Politica"),
("Giurisprudenza", "Diritto Internazionale"),
("Giurisprudenza", "Diritto del Lavoro"),
("Giurisprudenza", "Diritto Civile"),
("Giurisprudenza", "Diritto Penale"),
("Filosofia", "Storia Moderna"),
("Filosofia", "Paradigmi di razionalità pratica"),
("Filosofia", "Antropologia culturale"),
("Filosofia", "Entropsichiatria"),
("Filosofia", "Filosofia Morale"),
("Filosofia", "Culture e religioni del mondo antico"),
("Fisica", "Fisica I"),
("Fisica", "Laboratorio I"),
("Fisica", "Fisica II"),
("Fisica", "Laboratorio II"),
("Fisica", "Fisica III"),
("Fisica", "Laboratorio III"),
("Economia", "Economia Aziendale"),
("Economia", "Matematica Generale"),
("Economia", "Diritto Commerciale"),
("Economia", "Economia Industriale"),
("Economia", "Diritto Tributario"),
("Economia", "Programmazione e Controllo");


INSERT INTO Aule (nome, posti_totali) VALUES
("A0", 200),
("A1", 50),
("A2", 150),
("A3", 50);

INSERT INTO Lezioni (data, ora, descrizione, posti_disponibili, nome_materia, nome_aula, nome_professore, cognome_professore) VALUES
("2024-12-12", "11:00 - 13:00", "Puntatori in C", 200, "Programmazione Procedurale", "A0", "Francesco", "Santini"),
("2024-12-13", "12:00 - 14:00", "Ereditarietà in Java", 200, "Programmazione ad Oggetti", "A0", "Stefano", "Marcugini"),
("2024-12-14", "11:00 - 13:00", "Quicksort, complessità e efficienza", 150, "Algoritmi e Strutture Dati", "A2", "Maria Cristina", "Pinotti"),
("2024-12-15", "14:00 - 16:00", "Gli stati dei processi", 150, "Sistemi Operativi", "A2", "Arturo", "Carpi"),
("2024-12-16", "16:00 - 18:00", "Introduzione su Unity e Blender", 200, "Sistemi di realtà virtuale", "A0", "Osvaldo", "Gervasi"),
("2024-12-17", "09:00 - 11:00", "La normalizzazione delle basi di dati", 200, "Basi di dati", "A0", "Raffaella", "Gentilini"),
("2024-12-12", "11:00 - 13:00", "Funzioni in R", 50, "Analisi I", "A3", "Paola", "Rubbioni"),
("2024-12-13", "12:00 - 14:00", "I quadrati", 50, "Geometria I", "A1", "Daniele", "Bartoli"),
("2024-12-14", "11:00 - 13:00", "Integrali doppi", 150, "Analisi II", "A2", "Paola", "Rubbioni"),
("2024-12-15", "14:00 - 16:00", "Le matrici e i determinanti", 150, "Geometria II", "A2", "Daniele", "Bartoli"),
("2024-12-16", "16:00 - 18:00", "Le serie non lineari", 50, "Analisi III", "A3", "Paola", "Rubbioni"),
("2024-12-17", "09:00 - 11:00", "I numeri immaginari", 50, "Geometria III", "A1", "Daniele", "Bartoli"),
("2024-12-12", "11:00 - 13:00", "La tavola periodica", 200, "Chimica e Biochimica I", "A0", "Lorenzo", "Capoccioni"),
("2024-12-13", "12:00 - 14:00", "Le cellule", 200, "Istologia ed embriologia umana", "A0", "Roberta", "Cruschi"),
("2024-12-14", "11:00 - 13:00", "I batteri", 200, "Microbiologia", "A0", "Roberta", "Cruschi"),
("2024-12-15", "14:00 - 16:00", "I muscoli", 200, "Fisiologia", "A0", "Lorenzo", "Capoccioni"),
("2024-12-16", "16:00 - 18:00", "Esperimenti", 200, "Medicina di laboratorio", "A0", "Lorenzo", "Capoccioni"),
("2024-12-17", "09:00 - 11:00", "Le malattie", 200, "Patologia Sistemica", "A0", "Lorenzo", "Capoccioni"),
("2024-12-12", "11:00 - 13:00", "Cosa vuol dire diritto", 150, "Filosofia del Diritto", "A2", "Stefania", "Stefanelli"),
("2024-12-13", "12:00 - 14:00", "Le tasse italiane", 150, "Economia Politica", "A2", "Stefania", "Stefanelli"),
("2024-12-14", "11:00 - 13:00", "Relazioni internazionali", 150, "Diritto Internazionale", "A2", "Stefania", "Stefanelli"),
("2024-12-15", "14:00 - 16:00", "Il rapporto tra dipendente e imprenditore", 150, "Diritto del Lavoro", "A2", "Stefania", "Stefanelli"),
("2024-12-16", "16:00 - 18:00", "Il delitto", 150, "Diritto Civile", "A2", "Stefania", "Stefanelli"),
("2024-12-17", "09:00 - 11:00", "La prigione", 150, "Diritto Penale", "A2", "Stefania", "Stefanelli"),
("2024-12-12", "11:00 - 13:00", "La guerra fredda", 50, "Storia Moderna", "A1", "Maria", "Graziosi"),
("2024-12-13", "12:00 - 14:00", "La ragione", 50, "Paradigmi di razionalità pratica", "A1", "Maria", "Graziosi"),
("2024-12-14", "11:00 - 13:00", "L'umanità", 50, "Antropologia culturale", "A3", "Gianfranco", "Baldini"),
("2024-12-15", "14:00 - 16:00", "Il nostro essere interiore", 50, "Entropsichiatria", "A1", "Maria", "Graziosi"),
("2024-12-16", "16:00 - 18:00", "La correttezza delle nostre azioni", 50, "Filosofia Morale", "A3", "Gianfranco", "Baldini"),
("2024-12-17", "09:00 - 11:00", "Il cristianesimo", 50, "Culture e religioni del mondo antico", "A3", "Gianfranco", "Baldini"),
("2024-12-12", "11:00 - 13:00", "Le leggi della dinamica", 150, "Fisica I", "A2", "Gino", "Tosti"),
("2024-12-13", "12:00 - 14:00", "Il piano inclinato", 200, "Laboratorio I", "A0", "Gino", "Tosti"),
("2024-12-14", "11:00 - 13:00", "Meccanica", 50, "Fisica II", "A3", "Gino", "Tosti"),
("2024-12-15", "14:00 - 16:00", "Simulazione esame", 150, "Laboratorio II", "A2", "Gino", "Tosti"),
("2024-12-16", "16:00 - 18:00", "Il caso SpaceX", 150, "Laboratorio III", "A2", "Gino", "Tosti"),
("2024-12-17", "09:00 - 11:00", "Meccanica quantistica", 200, "Fisica III", "A0", "Gino", "Tosti"),
("2024-12-12", "11:00 - 13:00", "Il funzionamento delle aziende", 200, "Economia Aziendale", "A0", "Sonia", "Tulli"),
("2024-12-13", "12:00 - 14:00", "La proprietà commutativa", 200, "Matematica Generale", "A0", "Luca", "Franchi"),
("2024-12-14", "11:00 - 13:00", "Gli sconti", 150, "Diritto Commerciale", "A2", "Luca", "Franchi"),
("2024-12-15", "14:00 - 16:00", "Le nuove industrie", 200, "Economia Industriale", "A0", "Sonia", "Tulli"),
("2024-12-16", "16:00 - 18:00", "I tributi", 150, "Diritto Tributario", "A2", "Sonia", "Tulli"),
("2024-12-17", "09:00 - 11:00", "Le variabili", 150, "Programmazione e Controllo", "A2", "Luca", "Franchi");
