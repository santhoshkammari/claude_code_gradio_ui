import imaplib
import email
import itertools
import smtplib
import sys
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os
import mimetypes
import time
import logging
from typing import Optional,List

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Spinner:
    def __init__(self, message=""):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.message = message
        self.running = False
        self.spinner_thread = None

    def spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()

    def stop(self):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()


class GmailAutomation:
    def __init__(self, response_func=None, email_address='ailite.llm@gmail.com', app_password='aufu lhuc zomv ndil'):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = "imap.gmail.com"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.response_func = response_func
        self.ignore_emails = [
            "noreply",
            "no-reply",
            "googlecommunityteam",
            "google-noreply",
            "googleplay-noreply"
        ]

    def should_process_email(self, sender):
        """Check if we should process this email"""
        return not any(ignore in sender.lower() for ignore in self.ignore_emails)

    def attach_file(self, msg, file_path):
        """Attach a file to the email message based on its type"""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return False

        # Get the MIME type of the file
        mime_type, _ = mimetypes.guess_type(file_path)

        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # Handle different file types
            if mime_type is None:
                # If MIME type is unknown, treat as application/octet-stream
                attachment = MIMEApplication(file_data, _subtype='octet-stream')
            elif mime_type.startswith('image'):
                # Handle images
                attachment = MIMEImage(file_data, _subtype=mime_type.split('/')[-1])
            else:
                # Handle other file types (including PDFs)
                main_type, sub_type = mime_type.split('/')
                attachment = MIMEApplication(file_data, _subtype=sub_type)

            # Add header with filename
            filename = os.path.basename(file_path)
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)
            return True

        except Exception as e:
            logger.error(f"Error attaching file {file_path}: {e}")
            return False

    def check_emails(self):
        """Check for new emails and process them"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')

            _, messages = mail.search(None, 'UNSEEN')

            for msg_num in messages[0].split():
                try:
                    _, msg = mail.fetch(msg_num, '(RFC822)')
                    email_body = msg[0][1]
                    email_message = email.message_from_bytes(email_body)

                    sender = email.utils.parseaddr(email_message['From'])[1]

                    if self.should_process_email(sender):
                        subject = email_message['Subject']

                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = email_message.get_payload(decode=True).decode()

                        response = self.response_func(subject, body,sender)
                        if isinstance(response,tuple):
                            attachments = response[1]
                            response = response[0]
                        else:
                            attachments = None

                        self.send(
                            f"Re: {subject}",
                            f"Thank you for your email!\n\nYou sent: {body}\n\nAutomatic response: {response}\n\nBest regards,\nEmail Bot",
                            to_email=sender,
                            attachments=attachments
                        )

                        logger.info(f"Processed email from {sender}")
                    else:
                        logger.debug(f"Skipping system email from {sender}")

                except Exception as e:
                    logger.error(f"Error processing individual email: {e}")

            mail.logout()
            return "Email check completed successfully"

        except Exception as e:
            logger.error(f"Error in check_emails: {e}")
            return f"Error: {str(e)}"

    def send(self, subject, message, to_email='santhoshkammari1999@gmail.com', attachments=None):
        """Send email with optional attachments"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            # Handle attachments
            if attachments:
                # Convert single path to list for consistent handling
                if isinstance(attachments, str):
                    attachments = [attachments]

                # Attach each file
                for file_path in attachments:
                    success = self.attach_file(msg, file_path)
                    if success:
                        logger.info(f"Successfully attached: {file_path}")
                    else:
                        logger.warning(f"Failed to attach: {file_path}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.app_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def start(self, sleep_time=2):
        print("Email bot is running. Send a test email to ailite.llm@gmail.com ...")
        print('')
        spinner = Spinner("Checking for new emails...")

        try:
            spinner.start()
            while True:
                self.check_emails()
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            spinner.stop()
            print("\nBot stopped by user")
            sys.exit(0)


def automail(func, sleep_time=2):
    gmail = GmailAutomation(func)
    gmail.start(sleep_time=sleep_time)


def gmail(body, subject="AiLite Email", to_email='santhoshkammari1999@gmail.com', attachments=None):
    gmail = GmailAutomation()
    return gmail.send(subject=subject, message=body, to_email=to_email, attachments=attachments)

# FastMCP exposure: provide a single tool `gmail_send`
mcp = FastMCP("Gmail Server")

@mcp.tool
def gmail_send(subject: str, body: str, to: Optional[str] = None, attachments: Optional[List[str]] = None):
    """Send an email via Gmail. Only subject and body are required.

    Optional:
    - to: recipient email; if omitted, uses the default in GmailAutomation.
    - attachments: list of file paths to attach to the email
    """
    ga = GmailAutomation()
    to_email = to if to else 'santhoshkammari1999@gmail.com'
    ok = ga.send(subject=subject, message=body, to_email=to_email, attachments=attachments)
    return {"ok": bool(ok), "to": to_email, "subject": subject, "attachments": attachments or []}

tool_functions = {
    "gmail_send": gmail_send,
}

if __name__ == "__main__":
    mcp.run()

