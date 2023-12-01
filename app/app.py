#!/usr/bin/env python3

import os

import time, socket, imaplib, traceback
from imap_tools import MailBox, A, MailboxLoginError, MailboxLogoutError, MailMessageFlags

import smtplib
from email.message import EmailMessage

import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class httprint_mail_bot():
    def __init__(self, conf: dict):
        # Initialize the class.
        super().__init__()

        self.conf = conf
        self.httprint_host = conf.get("httprint-host")

        self.IMAPHOST = self.conf.get("imap-host")
        self.IMAPUSERNAME = self.conf.get("imap-username")
        self.IMAPPASSWORD = self.conf.get("imap-password")
        self.IMAPFOLDER = self.conf.get("imap-folder")
        self.SMTPHOST = self.conf.get("smtp-host")
        self.SMTPUSERNAME = self.conf.get("smtp-username")
        self.SMTPPASSWORD = self.conf.get("smtp-password")
        self.SMTPFROM = self.conf.get("smtp-from")

        self.mailbox = None

    def start(self):
        while True:
            try:
                with MailBox(self.IMAPHOST).login(self.IMAPUSERNAME, self.IMAPPASSWORD, self.IMAPFOLDER) as self.mailbox:
                    self.fetchmails()
            
                    responses = self.mailbox.idle.wait(timeout=300)
                    if responses:
                        self.fetchmails()
                    else:
                        logger.debug('No updates in 300 sec')

            except (TimeoutError, ConnectionError,
                    imaplib.IMAP4.abort, MailboxLoginError, MailboxLogoutError,
                    socket.herror, socket.gaierror, socket.timeout) as e:
                logger.info(f'## Error\n{e}\n{traceback.format_exc()}\nreconnect in a minute...')
                time.sleep(60)


    def fetchmails(self):
        mails = self.mailbox.fetch(A(seen=False), mark_seen=False)
        for mail in mails:

            for att in mail.attachments:

                fname = att.filename
                if not att.content_type == "application/pdf":
                    continue
                    
                logger.info(f"Document {fname} received")
                logger.debug(f"Subject {mail.subject}")

                files = {'file': (fname, att.payload)}

                params = self.parseopt(mail.subject)
                
                url = self.httprint_host + '/api/upload'
                try:
                    r = requests.post(url, files=files, params = params)
                    icon = "❌" if r.json().get("error") else "✅"
                    msg = f"{icon} {r.json().get('message')}"
                except requests.exceptions.RequestException as e:
                    msg = "🛑 Server error. Retry later"

                # send reply mail
                try:
                    with smtplib.SMTP_SSL(self.SMTPHOST) as server:
                        server.login(self.SMTPUSERNAME, self.SMTPPASSWORD)
                        reply = EmailMessage()
                        reply['From'] = self.SMTPFROM
                        reply['To'] = mail.reply_to or mail.from_

                        # reply['Subject'] = f"Re: {mail.subject}"
                        # reply["In_Reply-To"] = mail.headers['message-id'][0]
                        # # reply["References"] = (mail.headers["references"][0] or "") + " " + mail.headers["message-id"][0]

                        reply['Subject'] = msg
                        # reply.set_content(msg)

                        server.send_message(reply)
                except smtplib.SMTPException:
                    pass

                logger.info(msg)

            self.mailbox.delete(mail.uid)
            # self.mailbox.flag(mail.uid, MailMessageFlags.SEEN, True)




    def parseopt(self, optstr):
        if not optstr:
            return({})
        opts = optstr.lower().split()
        
        d = {}
        for opt in opts:
            match opt:
                case "single" | "one":
                    d["sides"] = "one-sided"
                case "long" | "2l" | "2long" | "twol" | "duplex" | "two":
                    d["sides"] = "two-sided-long-edge"
                case "short" | "2s" | "2short" | "twos":
                    d["sides"] = "two-sided-short-edge"
                case "a3" | "a4" | "a5":
                    d["media"] = opt.upper()
                case "mono" | "gray" | "black" | "bw":
                    d["color"] = "false"
                case "color" | "col" | "rgb" | "cmyk":
                    d["color"] = "true"
                case _:
                    if opt.isnumeric():
                        d["copies"] = int(opt)
        return(d)





if __name__ == '__main__':
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    logging.basicConfig(level=log_level)
    # logging.getLogger('telegram').setLevel(logging.WARNING)
    # logging.getLogger('httpx').setLevel(logging.WARNING)
    # logging.getLogger('httpcore').setLevel(logging.WARNING)

    config = {}
    config["httprint-host"] = os.environ.get("HTTPRINT_HOST", "http://httprint:7777")
    config["imap-host"] = os.environ.get("IMAP_HOST", "")
    config["imap-username"] = os.environ.get("IMAP_USERNAME", "")
    config["imap-password"] = os.environ.get("IMAP_PASSWORD", "")
    config["imap-folder"] = os.environ.get("IMAP_FOLDER", "INBOX")
    config["smtp-host"] = os.environ.get("SMTP_HOST", "")
    config["smtp-username"] = os.environ.get("SMTP_USERNAME", config["imap-username"])
    config["smtp-password"] = os.environ.get("SMTP_PASSWORD", config["imap-password"])
    config["smtp-from"] = os.environ.get("SMTP_FROM", config["smtp-username"])

    HMB = httprint_mail_bot(config)
    HMB.start()