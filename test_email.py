import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAIL_USERNAME = "olenka161991@gmail.com"   # той самий, що в .env MAIL_USERNAME
MAIL_PASSWORD = "gllfokjqrfieizeh"

def send_test_email():
    msg = MIMEText("Це тестовий лист для перевірки налаштувань SMTP.")
    msg['Subject'] = "Тестовий лист"
    msg['From'] = MAIL_USERNAME
    msg['To'] = MAIL_USERNAME  # можна відправити собі

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS шифрування
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, MAIL_USERNAME, msg.as_string())
        print("Лист успішно відправлено!")
    except smtplib.SMTPAuthenticationError:
        print("Помилка автентифікації: перевір пароль і логін.")
    except Exception as e:
        print(f"Інша помилка: {e}")

if __name__ == "__main__":
    send_test_email()
