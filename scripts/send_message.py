import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
from scripts.api_keys import app_pass

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
    msg['From'] = "yan.notebook.dex@yandex.ru"
    msg['To'] = email
    msg['Subject'] = TITLE
    msg.attach(MIMEText(BODY, 'plain'))
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login('yan.notebook.dex@yandex.ru', app_pass)
    server.sendmail('yan.notebook.dex@yandex.ru', email, msg.as_string())
    server.quit()
    return CODE
