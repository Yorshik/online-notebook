import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("yandex.notebook@gmail.com", "3113241009311313")

TITLE = 'Восстановление пароля'
BODY = f'''
Здравствуйте, вы запросили восстановление пароля
Код для восстановления: {"".join(map(str, [randint(0, 9) for _ in range(6)]))}
Если вы не запрашивали восстановление - проигнорируйте сообщение
Яндекс.Блокнот 
'''


def send_msg(email):
    msg = MIMEMultipart()
    msg['From'] = "your_email@gmail.com"
    msg['To'] = "recipient_email@example.com"
    msg['Subject'] = TITLE
    msg.attach(MIMEText(BODY, 'plain'))
    text = msg.as_string()
    server.sendmail("yandex.notebook@gmail.com", email, text)
