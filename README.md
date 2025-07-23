# Prenota Posto lezione
Progetto 10.1 del corso di Ingegneria del Software, anno accademico 2023/2024.

**10.1 Ricerca e prenotazione posto Lezione in presenza tramite bot**  
Lo studente registrato nel sistema può listare le lezioni disponibili che avranno un “id”, “descrizione”, “data-ora”, “aula” e prenotare un posto a lezione, se ancora disponibile. Considerare/Progettare meccanismo per evitare truffe e identificare utente

### Autori:
- Miriam Calandri
- Stefania Fiorelli

## Installare Python
- Versione utilizzata: 3.10

## Installare i requisiti
- All'interno del proprio ambiente di programmazione, eseguire il comando:
```bash
pip install -r requirements.txt
```
## Creare il database
- Il bot supporta [SQLiteCloud](https://www.sqlite.ai/)
- Le istruzioni sono presenti nel file [database.sql](/database/database.sql)

## Creare un file .env con le configurazioni
```env
TOKEN = "insert-your-telegram-bot-token"
EMAIL_PASSWORD = "insert-your-google-app-email-password"
CONN_DB = "inser-your-sqlite-db-connection-string"
```
## Avviare il bot
```bash
python3 main.py
```
Per terminare il programma è sufficiente interrompere l'esecuzione con CTRL+C.





