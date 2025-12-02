import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ----------------------------------------
# CONFIGURACIÓN
# ----------------------------------------
gmail_user = "gabriel.palomeque@ucb.edu.bo"
gmail_password = "aapu lkiq rchz uuwr"  # NO la normal

destinatario = "franco.morales@ucb.edu.bo"

asunto = "Alerta Raspi 5"
mensaje = "No hay marcadores"

# ----------------------------------------
# ARMAR EL CORREO
# ----------------------------------------
msg = MIMEMultipart()
msg["From"] = gmail_user
msg["To"] = destinatario
msg["Subject"] = asunto

msg.attach(MIMEText(mensaje, "plain"))

# ----------------------------------------
# ENVIAR
# ----------------------------------------
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(gmail_user, destinatario, msg.as_string())
    server.quit()
    
    print("Correo enviado con éxito.")

except Exception as e:
    print("Error al enviar correo:", e)