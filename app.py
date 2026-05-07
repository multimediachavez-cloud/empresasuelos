import os
import smtplib
from email.message import EmailMessage

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "cpgsuelosypavimentos@gmail.com")


def send_contact_email(nombre, correo, telefono, mensaje):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or COMPANY_EMAIL)
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    if not smtp_host or not smtp_user or not smtp_password:
        raise RuntimeError("SMTP no configurado en el servidor")

    email = EmailMessage()
    email["Subject"] = f"Nuevo mensaje web de {nombre}"
    email["From"] = smtp_from
    email["To"] = COMPANY_EMAIL
    email["Reply-To"] = correo
    email.set_content(
        "\n".join(
            [
                "Nuevo mensaje enviado desde la pagina web.",
                "",
                f"Nombre: {nombre}",
                f"Correo: {correo}",
                f"Telefono: {telefono or 'No indicado'}",
                "",
                "Mensaje:",
                mensaje,
            ]
        )
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        if smtp_use_tls:
            smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(email)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/servicios")
def servicios():
    return render_template("servicios.html")

@app.route("/proyectos")
def proyectos():
    return render_template("proyectos.html")

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        nombre = data.get("nombre", "").strip()
        correo = data.get("correo", "").strip()
        telefono = data.get("telefono", "").strip()
        mensaje = data.get("mensaje", "").strip()

        if not nombre or not correo or not mensaje:
            return jsonify({"message": "Completa nombre, correo y mensaje."}), 400

        try:
            send_contact_email(nombre, correo, telefono, mensaje)
        except Exception:
            app.logger.exception("No se pudo enviar el correo de contacto")
            return (
                jsonify(
                    {
                        "message": "No se pudo enviar el correo. Revisa la configuracion SMTP en Render."
                    }
                ),
                500,
            )

        return jsonify({"message": "Mensaje enviado correctamente al correo de la empresa."})

    return render_template("contacto.html")

if __name__ == "__main__":
    app.run(debug=True)
