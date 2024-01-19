import pymysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Параметры подключения к БД
host = '127.0.0.1'
port = 3306
user = 'mysql'
password = 'mysql'
database = 'twobd'

# Подключение к БД
con = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

# Запрос для получения максимального числа из столбцов move_in и move_out
query = "SELECT GREATEST(max(move_in), max(move_out)) AS max_number FROM users"

# Выполнение запроса
with con.cursor() as cursor:
    cursor.execute(query)
    result = cursor.fetchone()

# Закрытие соединения с БД
con.close()

# SMTP-сервер и порт
smtp_server = 'smtp.mail.ru'
smtp_port = 465

# Аккаунт отправителя
sender_email = 'kirill.ermolaev01@mail.ru'
sender_password = 'cUfVaqJLhwZQWCdmxxwz'

# Аккаунт получателя
recipient_email = 'mr.kir141@gmail.com'

# Подключение к SMTP-серверу
server = smtplib.SMTP_SSL(smtp_server, smtp_port)
server.login(sender_email, sender_password)

# Создание MIMEMultipart объекта
msg = MIMEMultipart()

# Добавление заголовка письма
msg['Subject'] = 'Максимальное число'

# Создание текстового содержимого письма
text = "Максимальное число: {}".format(result[0])
part = MIMEText(text, 'plain')
msg.attach(part)

# Отправка письма
server.sendmail(sender_email, recipient_email, msg.as_string())

# Закрытие соединения с SMTP-сервером
server.quit()
