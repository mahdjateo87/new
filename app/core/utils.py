from __future__ import annotations

import os
import smtplib
import subprocess
import webbrowser
from email.message import EmailMessage
from pathlib import Path


def open_file(path: Path) -> None:
    path = Path(path)
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        try:
            subprocess.run(["xdg-open", str(path)], check=False)
        except Exception:
            webbrowser.open(path.as_uri())


def print_file(path: Path) -> None:
    path = Path(path)
    if os.name == "nt":
        os.startfile(str(path), "print")  # type: ignore[attr-defined]
    else:
        open_file(path)


def send_email_with_attachments(
    smtp_config: dict,
    to_email: str,
    subject: str,
    body: str,
    attachments: list[Path],
) -> None:
    if not smtp_config.get("server") or not smtp_config.get("email"):
        raise ValueError("Configuration SMTP incomplète. Renseignez le serveur et l'email dans Paramètres.")

    message = EmailMessage()
    message["From"] = smtp_config["email"]
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    for attachment in attachments:
        data = Path(attachment).read_bytes()
        message.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=Path(attachment).name,
        )

    port = int(smtp_config.get("port", 587))
    with smtplib.SMTP(smtp_config["server"], port, timeout=30) as server:
        if smtp_config.get("use_tls", True):
            server.starttls()
        if smtp_config.get("password"):
            server.login(smtp_config["email"], smtp_config["password"])
        server.send_message(message)
