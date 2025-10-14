# gmailenvio.py
import smtplib
from email.mime.text import MIMEText

def enviar_correo(asunto="Mensaje desde Raspberry Pi", cuerpo="Hola, esta es la información que solicitaste."):
    remitente = "dsamuelguzman26@gmail.com"
    destinatario = "dsamuelguzman@gmail.com"
    contraseña = "obpoodvsnyokguvn"  # los 16 caracteres (app password de Gmail)

    # Crear el mensaje
    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    # Enviar el correo
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)
        servidor.quit()
        print("✅ Correo enviado exitosamente.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)
