import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint


def send(email: str) -> str:
    TITLE = 'Восстановление пароля'
    CODE = "".join(map(str, [randint(0, 9) for _ in range(6)]))
    BODY = f'''
    Здравствуйте, вы запросили восстановление пароля
    Код для восстановления: {CODE} 
    Если вы не запрашивали восстановление - проигнорируйте сообщение
    Яндекс.Блокнот 
    '''
    from_addr = 'yan.notebook.dex@yandex.ru'
    password = 'xngxrjcdhxrotjie'
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = email
    msg['Title'] = TITLE
    msg.attach(MIMEText(BODY, 'plain'))
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.starttls()
    server.login(from_addr, password)
    server.send_message(msg)
    return CODE
