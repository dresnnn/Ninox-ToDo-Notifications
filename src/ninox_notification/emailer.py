import smtplib
from email.message import EmailMessage
from typing import List
from .config import SMTPConfig


class Emailer:
    def __init__(self, config: SMTPConfig, debug: bool = False):
        self.config = config
        self.debug = debug

    def send(self, recipient: str, subject: str, html_body: str, *, force_send: bool = False):
        msg = EmailMessage()
        msg["From"] = self.config.from_address
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(html_body, subtype="html")

        if self.debug and not force_send:
            print(f"[DEBUG] Would send email to {recipient}: {subject}")
            return

        with smtplib.SMTP(self.config.host, self.config.port) as smtp:
            smtp.starttls()
            if self.config.username and self.config.password:
                smtp.login(self.config.username, self.config.password)
            smtp.send_message(msg)
