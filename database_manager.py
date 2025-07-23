from os import getenv
from sqlitecloud import connect
from dotenv import load_dotenv
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.connection_string = getenv("CONN_DB")
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = connect(self.connection_string)

    def get_courses(self) -> list:
        query = self.connection.execute("SELECT nome FROM CorsiDiLaurea")
        query_result = query.fetchall()

        result = []
        for tuple in query_result:
            result.append(tuple[0])
        return result

    def get_lessons(self, email: str) -> list:
        query = self.connection.execute("SELECT nome_corso,anno_di_corso FROM Utenti WHERE ?=email", (email,))
        info_course = query.fetchone()

        today = datetime.today()
        next_week = today + timedelta(days=7)
        today = today.strftime("%Y-%m-%d")
        next_week = next_week.strftime("%Y-%m-%d")

        course_subjects = f"SELECT nome_materia FROM Insegnamenti WHERE '{info_course[0]}'=nome_corso"
        subjects_year = f"SELECT nome FROM Materie WHERE nome IN({course_subjects}) AND {info_course[1]}=anno_di_corso"
        query = self.connection.execute(f"SELECT * FROM Lezioni WHERE nome_materia IN({subjects_year}) AND data BETWEEN '{today}' AND '{next_week}' ORDER BY data, ora") 
        lessons = query.fetchall()
        return lessons

    def get_lesson_details(self, lesson_id: int) -> list:
        query = self.connection.execute("SELECT * FROM Lezioni WHERE ?=id_lezione", (lesson_id,))
        lesson_details = query.fetchone()
        return lesson_details

    def get_user_info(self, email:str) -> list:
        query = self.connection.execute("SELECT * FROM Utenti WHERE ?=email", (email,))
        info_utente = query.fetchone()
        return info_utente
        
    def check_email(self, email: str) -> bool:
        query = self.connection.execute("SELECT * FROM Utenti WHERE ?=email", (email,))
        query_result = query.fetchall()
        
        if not query_result:
            return False
        else:
            return True 

    def insert_user(self, nome: str, cognome: str, email: str, anno:int, corso: str):
        insert = "INSERT INTO Utenti(nome, cognome, email, anno_di_corso, nome_corso) VALUES (?, ?, ?, ?, ?);"
        self.connection.execute(insert, (nome, cognome, email, anno, corso))

    def is_user_booked(self, email: str, lesson_id: int) -> list:
        search = "SELECT id_prenotazione FROM Prenotazioni WHERE ?=id_lezione AND ?=email_utente"
        query = self.connection.execute(search, (lesson_id, email))
        result = query.fetchone()

        if result is None:
            return -1
        else:
            return result[0]
        
    def get_bookings(self, email: str) -> list:
        search = "SELECT * FROM Prenotazioni p, Lezioni l WHERE ?=email_utente AND p.id_lezione=l.id_lezione ORDER BY l.data, l.ora"
        query = self.connection.execute(search, (email,))
        bookings = query.fetchall()
        return bookings

    def get_booking_details(self, booking_id: int) -> list:
        query = self.connection.execute("SELECT * FROM Prenotazioni WHERE ?=id_prenotazione", (booking_id,))
        booking_details = query.fetchone()
        return booking_details

    def insert_booking(self, lesson_id: int, email: str):
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M")

        insert = "INSERT INTO Prenotazioni(data, ora, id_lezione, email_utente) VALUES (?, ?, ?, ?);"
        update = f"UPDATE Lezioni SET posti_disponibili=posti_disponibili-1 WHERE {lesson_id}=id_lezione"
        self.connection.execute(insert, (date, time, lesson_id, email))
        self.connection.execute(update)

    def cancel_booking(self, booking_id: int, lesson_id: int):
        self.connection.execute(f"DELETE FROM Prenotazioni WHERE {booking_id}=id_prenotazione")
        self.connection.execute(f"UPDATE Lezioni SET posti_disponibili=posti_disponibili+1 WHERE {lesson_id}=id_lezione")