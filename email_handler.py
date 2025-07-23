from random import randint
from smtplib import SMTP_SSL
from ssl import create_default_context
from email.message import EmailMessage
from telegram.ext import ContextTypes
from os import getenv
from dotenv import load_dotenv

load_dotenv()
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")
EMAIL_SENDER = 'prenotapostolezione@gmail.com'

def verify_email(email: str, context:ContextTypes.DEFAULT_TYPE) -> bool:
    user_data = context.user_data

    code = randint(10000, 99999)
    user_data['codice'] = code
    print(f"Codice di verifica inviato a {email}: {code}")

    subject = "Verifica email"
    body = f"""
    Il codice di verifica è: 
    {code}
    """
    
    try:
        domain = email.split("@")
        if domain[1] == "studenti.unipg.it":
            em = EmailMessage()
            em['From'] = EMAIL_SENDER
            em['To'] = email
            em['Subject'] = subject
            em.set_content(body)
            context = create_default_context()
            with SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.sendmail(EMAIL_SENDER, email, em.as_string())
            print(f"Email inviata con successo a {email}")
            return True
        else: return False
        
    except Exception as e:
        print("Errore nella email: ", e)
        return False

        