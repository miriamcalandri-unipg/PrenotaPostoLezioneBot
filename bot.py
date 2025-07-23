import email_handler
import logging
import re
from enum import Enum
from datetime import datetime, timedelta
from re import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import ContextTypes, ConversationHandler

# Stato iniziale
START_MENU = 0

# Stati registrazione 
PROCESSING_DATA, VERIFYING_EMAIL, CONFIRMATION, CHOSEN_COURSE = range(1, 5) 
states = Enum('Stato', ['NOME', 'COGNOME', 'EMAIL_DA_VERIFICARE', 'VERIFICA_EMAIL', 'SCELTA_CORSO', 'ANNO_CORSO'])

# Stati login
AUTHENTICATION, MAIN_MENU = range(5, 7)

# Logger
logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y/%m/%d - %H:%M:%S", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, database):
        self.database = database

    """
    Chiamata quando l'utente avvia la conversazione. 
    Resetta l'user_data dell'utente e memorizza l'id della chat.
    L'utente può registrarsi o eseguire il login.
    """
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user

        user_data = context.user_data
        user_data.clear()
        user_data['chat_id'] = update.effective_user.id

        logger.info("User %s ha iniziato una conversazione", user.first_name)
        
        keyboard = [
            [
                InlineKeyboardButton("Registrati", callback_data="registrazione"),
                InlineKeyboardButton("Login", callback_data="login"),
            ]
        ]
        buttons = InlineKeyboardMarkup(keyboard)
        
        first_message_body = f"Benvenuto nel sistema di prenotazione delle lezioni, {user.first_name}!"
        second_message_body = f"Se già ci conosciamo, effettua il login per accedere, altrimenti seleziona Registrati per creare un account."
        await context.bot.send_message(chat_id=user_data['chat_id'], text=first_message_body)
        await context.bot.send_message(chat_id=user_data['chat_id'], text=second_message_body, reply_markup=buttons)
        return START_MENU


    """
    Chiamata quando l'utente preme il pulsante "Registrati", inizia il processo di registrazione.
    Aggiunge il campo 'stato' al dizionario user_data dell'utente e lo imposta allo stato di inserimento del nome.
    """
    async def register(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        user_data = context.user_data

        logger.info("User %s ha premuto registrati", user.first_name)
        
        query = update.callback_query
        body = f"{user.first_name}, iniziamo la registrazione!\nPer uscire dall'operazione di registrazione puoi eseguire il comando /exit"
        await query.answer()
        await query.edit_message_text(body)
        await context.bot.send_message(text = f"Scrivi il tuo nome", chat_id = user_data['chat_id'])
        
        user_data['stato'] = states.NOME.value
        return PROCESSING_DATA


    """
    Funzione che gestisce le informazioni inviate dall'utente, le memorizza e chiede conferma.
    """
    async def receive_information(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        user_data = context.user_data
        keyboard = [
            [
                InlineKeyboardButton("Conferma", callback_data="conferma"),
                InlineKeyboardButton("Indietro", callback_data="indietro")
            ]
        ] 
        buttons = InlineKeyboardMarkup(keyboard)

        """
        In base allo stato di registrazione dell'utente processa le informazioni ricevute e chiede conferma all'utente.
        """
        match user_data['stato']:
            case states.NOME.value:
                name = update.message.text
                if len(name) > 20 or len(name) < 3:
                    logger.info("Il nome %s inviato da user %s non è valido", name, user.first_name)
                    await update.message.reply_text(f"Il nome scelto è troppo lungo o troppo corto.\nInvia un nome di lunghezza compresa tra 3 e 20 caratteri.")
                    return PROCESSING_DATA
                
                user_data['nome'] = re.escape(name)
                logger.info("User %s ha inviato il suo nome: %s", user.first_name, name)
                await update.message.reply_text(f"Il tuo nome è: {name}.", reply_markup = buttons)
                return CONFIRMATION
            
            case states.COGNOME.value:
                surname = update.message.text
                if len(surname) > 20 or len(surname) < 3:
                    logger.info("Il cognome %s inviato da user %s non è valido", surname, user.first_name)
                    await update.message.reply_text(f"Il cognome scelto è troppo lungo o troppo corto.\nInvia un cognome di lunghezza compresa tra 3 e 20 caratteri.")
                    return PROCESSING_DATA
                
                user_data['cognome'] = re.escape(surname)
                logger.info("User %s ha inviato il suo cognome: %s", user.first_name, surname)
                await update.message.reply_text(f"Il tuo cognome è: {surname}.", reply_markup = buttons)
                return CONFIRMATION
            
            case states.EMAIL_DA_VERIFICARE.value:
                email = update.message.text.lower()
                user_data['email'] = email
                logger.info("User %s ha inviato la sua email: %s", user.first_name, email)
                
                is_email_registered = self.database.check_email(email)
                if is_email_registered:
                    logger.info("L'email %s inviata da %s è già registrata.", email, user.first_name)
                    await update.message.reply_text(f"L'email {email} è già registrata. Inseriscine un'altra.")
                    return PROCESSING_DATA
                
                await update.message.reply_text(f"La tua email è: {email}.", reply_markup = buttons)
                return CONFIRMATION
            
            case states.SCELTA_CORSO.value:
                query = update.callback_query
                corso = query.data
                user_data['corso'] = corso

                logger.info("User %s ha selezionato il corso %s", user.first_name, user_data['corso'])
                await query.answer()
                await query.edit_message_text(f"Hai selezionato il corso: {corso}.", reply_markup = buttons)
                return CONFIRMATION
            
            case states.ANNO_CORSO.value:
                anno = update.message.text
                
                try:
                    anno = int(anno)
                    if anno >= 1 and anno <= 3:
                        user_data['anno'] = anno
                        logger.info("User %s ha inserito l'anno di corso: %s", user.first_name, anno)
                        await update.message.reply_text(f"Sei nell'anno di corso: {anno}.", reply_markup = buttons)
                        return CONFIRMATION
                    else: raise ValueError
                except ValueError:
                    await update.message.reply_text(f"Anno non valido. Inserire un numero tra 1 e 3.")
                    return PROCESSING_DATA


    """
    Chiamata quando l'utente ha confermato l'informazione inserita,
    passa allo stato di registrazione successivo chiedendo l'informazione successiva.
    """
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_data = context.user_data
        query = update.callback_query
        await query.answer()

        """
        Se l'utente si trova sull'ultimo stato (inserimento dell'anno di corso), 
        lo inserisce nel database e termina la registrazione.
        """
        if user_data['stato'] == states.ANNO_CORSO.value:
            self.database.insert_user(user_data['nome'], user_data['cognome'], user_data['email'], int(user_data['anno']), user_data['corso'])

            await query.edit_message_text(f"Registrazione effettuata con successo.\nDigita il comando /start per fare il login.")
            return ConversationHandler.END
        
        else:
            user_data['stato'] += 1
            
            if user_data['stato'] == states.COGNOME.value:
                await query.edit_message_text(f"Scrivi il tuo cognome")
                return PROCESSING_DATA
            
            if user_data['stato'] == states.EMAIL_DA_VERIFICARE.value:
                await query.edit_message_text(f"Scrivi la tua email")
                return PROCESSING_DATA
            
            if user_data['stato'] == states.VERIFICA_EMAIL.value:
                is_email_valid = email_handler.verify_email(user_data['email'], context)
                if is_email_valid:
                    await query.edit_message_text(f"Scrivi il codice di verifica inviato alla tua email")
                    return VERIFYING_EMAIL
                else:
                    user_data['stato'] = states.EMAIL_DA_VERIFICARE.value
                    await query.edit_message_text(f"Email non valida, inserisci un'email istituzionale da studente UniPG")
                    return PROCESSING_DATA
            
            if user_data['stato'] == states.SCELTA_CORSO.value:
                keyboard = [[]]
                courses = self.database.get_courses()
                n_courses = len(courses)

                for i in range(n_courses):
                    keyboard[i//2].append(InlineKeyboardButton(courses[i], callback_data=courses[i]))
                    if i % 2 == 1 and i != n_courses - 1:
                        keyboard.append([])
            
                buttons = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"Seleziona il tuo corso di laurea", reply_markup=buttons)
                return CHOSEN_COURSE
            
            if user_data['stato'] == states.ANNO_CORSO.value:
                await query.edit_message_text(f"Scrivi l'anno di corso a cui sei iscritto")
                return PROCESSING_DATA


    """
    Chiamata quando l'utente annulla l'inserimento.
    Rimuove l'informazione appena inserita e la richiede all'utente.
    """
    async def go_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_data = context.user_data       
        query = update.callback_query
        
        if user_data['stato'] == states.NOME.value:
            del user_data['nome']
            await query.edit_message_text(f"Scrivi il tuo nome")
            return PROCESSING_DATA
        
        if user_data['stato'] == states.COGNOME.value:
            del user_data['cognome']
            await query.edit_message_text(f"Scrivi il tuo cognome")
            return PROCESSING_DATA
        
        if user_data['stato'] == states.EMAIL_DA_VERIFICARE.value:
            del user_data['email']
            await query.edit_message_text(f"Scrivi la tua email")
            return PROCESSING_DATA
        
        if user_data['stato'] == states.SCELTA_CORSO.value:
            query = update.callback_query
            course = query.data
            user_data['corso'] = course
            keyboard = [[]]
            courses = self.database.get_courses()
            n_courses = len(courses)

            for i in range(n_courses):
                keyboard[i//2].append(InlineKeyboardButton(courses[i], callback_data=courses[i]))
                if i % 2 == 1 and i != n_courses - 1:
                    keyboard.append([])
            
            buttons = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Seleziona il tuo corso di laurea", reply_markup=buttons)
            return CHOSEN_COURSE
        
        if user_data['stato'] == states.ANNO_CORSO.value:
            del user_data['anno']
            await query.edit_message_text(f"Scrivi l'anno di corso a cui sei iscritto")
            return PROCESSING_DATA


    """
    Controlla che il codice di verifica scritto dall'utente corrisponda a quello generato,
    sia nel caso del login che nel caso della registrazione.
    Se l'utente si sta registrando, continua la registrazione, altrimenti va al menu principale.
    """
    async def verify_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
            user = update.effective_user
            user_message = update.message.text
            user_data = context.user_data
            user_code = user_data['codice']

            logger.info("User %s ha scritto il codice %s", user.first_name, user_message)
            
            keyboard = [ [ InlineKeyboardButton("Continua", callback_data="conferma") ] ]
            buttons = InlineKeyboardMarkup(keyboard)
        
            return_states = [ PROCESSING_DATA, CONFIRMATION ]
            is_registering = 'stato' in user_data.keys()
            if not is_registering:
                return_states[0] = AUTHENTICATION
                return_states[1] = MAIN_MENU

            """
            Controlla se il codice è un numero e se è valido, 
            altrimenti rimuove l'email memorizzata precedentemente
            e chiede all'utente di riprovare con un'altra email
            """
            try:
                if int(user_message) == user_code:
                    logger.info("User %s ha verificato la sua email", user.first_name)
                    del user_data['codice']
                    
                    await update.message.reply_text(f"La tua email è stata verificata correttamente.", reply_markup=buttons)
                    return return_states[1]
                else: raise ValueError

            except ValueError:
                logger.info("User %s ha mandato un numero non valido", user.first_name)
                del user_data['codice']
                del user_data['email']

                if is_registering:
                    user_data['stato'] = states.EMAIL_DA_VERIFICARE.value
                
                await update.message.reply_text(f"La tua email non è stata verificata correttamente.")
                await update.message.reply_text(f"Inserisci un'altra email o reinserisci la stessa per riprovare.")
                return return_states[0]


    """
    Chiede all'utente di inviare l'email con cui è registrato per effettuare il login.
    """
    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        query = update.callback_query
        user_data = context.user_data
        user_data.clear()
        user_data['chat_id'] = update.effective_user.id
        
        logger.info("User %s ha premuto login", user.first_name)
        
        await query.answer()
        await query.edit_message_text(f"{user.first_name} invia l'email con cui ti sei registrato per effettuare il login.")
        return AUTHENTICATION


    """
    Contolla se l'email inserita dall'utente è registrata nel database,
    in caso affermativo invia un codice di verifica tramite email,
    altrimenti chiede all'utente di effettuare la registrazione
    """
    async def authentication(self, update:Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        email = update.message.text.lower()
        user_data = context.user_data
        user_data['email'] = email
        logger.info("User %s ha inviato la sua email: %s", user.first_name, email)
        
        is_email_registered = self.database.check_email(email)
        if is_email_registered:
            email_handler.verify_email(email, context)
            await context.bot.send_message(chat_id=user_data['chat_id'], text=f"Inserisci il codice di verifica inviato alla tua email.")
            return VERIFYING_EMAIL
        else:
            await context.bot.send_message(chat_id=user_data['chat_id'], text=f"Email non registrata. Digita /start per effettuare la registrazione.")
            return ConversationHandler.END
        

    """
    Menu principale per l'utente che ha effettuato il login,
    consente di visualizzare le lezioni o le prenotazioni.
    """
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        user_data = context.user_data

        """
        user_info contiene la lista dei campi dell'utente presa dal database:
        user_info[0] = email
        user_info[1] = nome 
        user_info[2] = cognome
        user_info[3] = anno di corso
        user_info[4] = nome corso
        """
        user_info = self.database.get_user_info(user_data['email'])
        user_data['nome'] = user_info[1]
        user_data['cognome'] = user_info[2]
        user_data['anno'] = user_info[3]
        user_data['corso'] = user_info[4]

        query = update.callback_query
        keyboard = [
            [
                InlineKeyboardButton("Visualizza lezioni", callback_data="visualizza_lezioni"),
                InlineKeyboardButton("Visualizza prenotazioni", callback_data="visualizza_prenotazioni")
            ]
        ]
        buttons = InlineKeyboardMarkup(keyboard)
        body = f"Bentornato *{user_data['nome']} {user_data['cognome']}\.*\n> *Email*: {re.escape(user_data['email'])}\n> *Corso*: {user_data['corso']}\n> *Anno*: {user_data['anno']}\nScrivere /exit per terminare la conversazione ed effettuare il logout\."
        
        logger.info("User %s sta visualizzando il menu principale", user.first_name)
        await query.answer()
        await query.edit_message_text(body, parse_mode=constants.ParseMode.MARKDOWN_V2, reply_markup=buttons)
        return MAIN_MENU


    """
    Elenca le lezioni, nell'arco di una settimana, alla quale l'utente può prenotarsi 
    in base al suo corso di laurea e anno di corso
    """
    async def list_lessons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_data = context.user_data
        query = update.callback_query
        user = update.effective_user
        lessons = self.database.get_lessons(user_data['email'])
        
        if not lessons:
            keyboard = []
            keyboard.append([InlineKeyboardButton("Indietro", callback_data="menu")])
            buttons = InlineKeyboardMarkup(keyboard)
            
            logger.info("User %s non ha lezioni disponibili.", user.first_name)
            await query.answer()
            await query.edit_message_text(f"Non ci sono lezioni disponibili.", reply_markup=buttons)
            return MAIN_MENU
        
        today = datetime.today()
        next_week = today + timedelta(days=7)

        today = today.strftime("%d/%m")
        next_week = next_week.strftime("%d/%m")
    
        """
        lessons è una lista che contiene una tupla per ogni lezione presente
        nel database. Per ogni lezione:
        lesson[0] = id_lezione
        lesson[1] = data
        lesson[2] = ora
        lesson[3] = descrizione
        lesson[4] = posti disponibili
        lesson[5] = nome della materia
        lesson[6] = nome dell'aula
        lesson[7] = nome del professore
        lesson[8] = cognome del professore
        """
        button_names = []
        for lesson in lessons:
            date = lesson[1].split("-")
            time = lesson[2].split("-")
            button_names.append(f"{date[2]}/{date[1]} ⌚ {time[0]} | {lesson[5]}")

        keyboard = []    
        for i,lesson in enumerate(lessons):
            callback_data = "lezione-" + str(lesson[0])
            keyboard.append([InlineKeyboardButton(button_names[i], callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("Indietro", callback_data="menu")])
        buttons = InlineKeyboardMarkup(keyboard)

        logger.info("User %s sta visualizzando le lezioni di %s dell'anno %s", user.first_name, user_data['corso'], user_data['anno'])
        await query.answer()
        await query.edit_message_text(f"Lezioni del corso {user_data['corso']}, anno {user_data['anno']}\nSettimana dal {today} al {next_week}", reply_markup=buttons)
        return MAIN_MENU


    """
    Mostra i dettagli della lezione selezionata
    """
    async def view_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        user = update.effective_user
        lesson_id = int(query.data.split("-")[1])
        user_data = context.user_data

        lesson_details = self.database.get_lesson_details(lesson_id)

        """
        lesson_details è una lista con i dettagli della lezione:
        lesson_details[0] = id_lezione
        lesson_details[1] = data
        lesson_details[2] = ora
        lesson_details[3] = descrizione
        lesson_details[4] = posti disponibili
        lesson_details[5] = nome della materia
        lesson_details[6] = nome dell'aula
        lesson_details[7] = nome del professore
        lesson_details[8] = cognome del professore
        """
        date = lesson_details[1].split("-")
        time = lesson_details[2].split("-")
        description = escape(lesson_details[3])
        seats = int(lesson_details[4])
        subject_name = lesson_details[5]
        professor = f"{lesson_details[7]} {lesson_details[8]}"
    
        """
        Se l'utente non è prenotato ritorna -1, 
        altrimenti ritorna l'id della prenotazione
        """
        booking_id = self.database.is_user_booked(user_data['email'], lesson_id)
        
        """
        Se sono presenti posti disponibili mostra un pulsante 'prenota' e 'indietro', 
        se l'utente è già prenotato alla lezione mostra un pulsante 'vedi prenotazione' e 'indietro',
        se l'utente non è prenotato e non ci sono posti disponibili mostra solo il pulsante 'indietro'
        """
        keyboard = [[]]
        if seats > 0:
            if booking_id == -1:
                prenota_lezione = "prenota-" + str(lesson_id)
                keyboard[0].append(InlineKeyboardButton("Prenota", callback_data=prenota_lezione))
            else:
                vedi_prenotazione = "prenotazione-" + str(booking_id)
                keyboard[0].append(InlineKeyboardButton("Vedi Prenotazione", callback_data=vedi_prenotazione))
        elif booking_id != -1:
            vedi_prenotazione = "prenotazione-" + str(booking_id)
            keyboard[0].append(InlineKeyboardButton("Vedi Prenotazione", callback_data=vedi_prenotazione))

        keyboard[0].append(InlineKeyboardButton("Indietro", callback_data="visualizza_lezioni"))  
        buttons = InlineKeyboardMarkup(keyboard)           
        
        logger.info("User %s sta visualizzando la lezione %s", user.first_name, lesson_id)
        body = f"*{subject_name}* \| {professor}\n📅 `{date[2]}/{date[1]}` ⌚`{time[0]}`\-`{time[1]}`\n> {description}\nPosti disponibili: `{seats}`"
        await query.answer()
        await query.edit_message_text(body, parse_mode=constants.ParseMode.MARKDOWN_V2, reply_markup=buttons)
        return MAIN_MENU


    """
    Mostra tutte le prenotazioni dell'utente
    """
    async def list_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        user = update.effective_user
        user_data = context.user_data
        bookings = self.database.get_bookings(user_data['email'])

        if not bookings:
            keyboard = []
            keyboard.append([InlineKeyboardButton("Indietro", callback_data="menu")])
            buttons = InlineKeyboardMarkup(keyboard)
            
            logger.info("User %s non ha prenotazioni.", user.first_name)
            await query.answer()
            await query.edit_message_text(f"Non ci sono prenotazioni.", reply_markup=buttons)
            return MAIN_MENU
        
        """
        bookings è una lista di tuple. Per ogni booking:
        booking[0] = id_prenotazione  
        booking[1] = data
        booking[2] = ora
        booking[3] = id_lezione
        booking[4] = email dell'utente

        In lessons viene salvata una lista di tuple con i dettagli di ogni lezione a cui l'utente è prenotato.
        """
        lessons = []
        for booking in bookings:
            lessons.append(self.database.get_lesson_details(booking[3]))
        
        keyboard = []
        button_names = []
        for i,lesson in enumerate(lessons):
            date = lesson[1].split("-")
            time = lesson[2].split("-")
            button_names.append(f"{date[2]}/{date[1]} ⌚ {time[0]} | {lesson[5]}")
            vedi_prenotazione = "prenotazione-" + str(bookings[i][0])
            keyboard.append([InlineKeyboardButton(button_names[i], callback_data=vedi_prenotazione)])
        keyboard.append([InlineKeyboardButton("Indietro", callback_data="menu")]) 
        buttons = InlineKeyboardMarkup(keyboard)  
        
        logger.info("User %s sta visualizzando le sue prenotazioni", user.first_name)
        await query.answer()
        await query.edit_message_text(f"Le tue prenotazioni", reply_markup=buttons)
        return MAIN_MENU


    """
    Prenota un posto alla lezione selezionata
    """
    async def book_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        user = update.effective_user
        data = query.data.split("-")
        lesson_id = data[1]
        user_data = context.user_data

        self.database.insert_booking(lesson_id, user_data['email'])

        keyboard = [[]]
        vedi_lezione = "lezione-" + lesson_id
        keyboard[0].append(InlineKeyboardButton("Indietro", callback_data=vedi_lezione)) 
        buttons = InlineKeyboardMarkup(keyboard) 

        logger.info("User %s ha prenotato la lezione con id %s", user.first_name, lesson_id)
        await query.answer()
        await query.edit_message_text(f"Prenotazione effettuata con successo.", reply_markup=buttons)
        return MAIN_MENU


    """
    Mostra i dettagli della prenotazione selezionata e della lezione corrispondente
    """
    async def view_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        user = update.effective_user
        booking_id = int(query.data.split("-")[1])

        booking_details = self.database.get_booking_details(booking_id)
        lesson_details = self.database.get_lesson_details(booking_details[3])
        
        book_date = booking_details[1].split("-")
        book_time = booking_details[2]
        
        date = lesson_details[1].split("-")
        time = lesson_details[2].split("-")
        description = escape(lesson_details[3])
        subject_name = lesson_details[5]
        professor = f"{lesson_details[7]} {lesson_details[8]}"

        annulla_prenotazione = "annulla-"+ str(booking_id) + "-" + str(lesson_details[0])
        keyboard = [[ InlineKeyboardButton("Annulla Prenotazione", callback_data=annulla_prenotazione), InlineKeyboardButton("Indietro", callback_data="visualizza_prenotazioni") ]]
        buttons = InlineKeyboardMarkup(keyboard)

        logger.info("User %s sta visualizzando la prenotazione %s", user.first_name, booking_id)
        body = f"Prenotazione avvenuta il `{book_date[2]}/{book_date[1]}` alle `{book_time}`\n*{subject_name}* \| {professor}\n📅 `{date[2]}/{date[1]}` ⌚`{time[0]}`\-`{time[1]}`\n> {description}"
        await query.answer()
        await query.edit_message_text(body, parse_mode=constants.ParseMode.MARKDOWN_V2, reply_markup=buttons)
        return MAIN_MENU

    """
    Annulla la prenotazione selezionata
    """
    async def cancel_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        query = update.callback_query
        booking_id = int(query.data.split("-")[1])
        lesson_id = int(query.data.split("-")[2])
        self.database.cancel_booking(booking_id, lesson_id)

        keyboard = [[]]
        keyboard[0].append(InlineKeyboardButton("Indietro", callback_data="visualizza_prenotazioni")) 

        buttons = InlineKeyboardMarkup(keyboard)  

        logger.info("User %s ha annullato la prenotazione %s", user.first_name, booking_id)
        await query.answer()
        await query.edit_message_text(f"Prenotazione annullata con successo.", reply_markup=buttons)
        return MAIN_MENU


    """
    Termina la conversazione e cancella i dati inseriti dall'utente
    """
    async def exit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        user_data = context.user_data
        user_data.clear()
        
        logger.info("User %s ha terminato la conversazione", user.first_name)
        await update.message.reply_text("Conversazione terminata. Digitare /start per ricominciare.")
        return ConversationHandler.END
