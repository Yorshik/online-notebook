import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("yandex.notebook@gmail.com", "3113241009311313")

TITLE = 'Восстановление пароля'
CODE = "".join(map(str, [randint(0, 9) for _ in range(6)]))
BODY = f'''
Здравствуйте, вы запросили восстановление пароля
Код для восстановления: {CODE}
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
    return CODE
