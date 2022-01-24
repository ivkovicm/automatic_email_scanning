import os
from smtpd import SMTPServer
from smtplib import SMTP

from user_modules import update_db
import asyncore
from eml_parser import EmlParser
import base64
import hashlib
import threading
from other import config_loader, custom_types, custom_errors, rabbit_manipulation, loger_setup


class MailConfigurations:
    def __init__(self, config: dict):
        self.email_path = ""
        self.manual_dir = ""
        self.ingress_port = ""
        self.egress_port = ""
        self.parse_config(config)

    def parse_config(self, config) -> None:
        self.email_path = config["SMTPServer"]["Eml_Path"]
        self.manual_dir = config["SMTPServer"]["Manual_Check"]
        self.ingress_port = config["SMTPServer"]["Ingress_Port"]
        self.egress_port = config["SMTPServer"]["Egress_Port"]
        self.check_config()

    def check_config(self) -> None:
        if self.ingress_port == "" or self.egress_port == "":
            logging.critical("Error in configuration file (check SMTP IPs and PORTs)!")
            raise custom_errors.SMTPConfigError
        elif self.email_path == "" or self.manual_dir == "":
            logging.critical("Error in configuration file (check SMTP mails folder path)!")
            raise custom_errors.SMTPConfigError
        elif not os.path.isdir(self.email_path) or not os.path.isdir():
            logging.critical("SMTP directories for saving mails doesn't exist!")
            raise custom_errors.SMTPMailDirsError


class EmailReceiver(SMTPServer):
    def __init__(self, config: MailConfigurations):
        self.config = config
        super(EMAILServer, self).__init__(("127.0.0.1", self.config.ingress_port), None)

    def process_message(self, peer, mailfrom, rcpttos, data, decode_data=False):

        mailfrom.replace("\'", "")
        mailfrom.replace("\"", "")

        for recipient in rcpttos:
            recipient.replace("\'", "")
            recipient.replace("\'", "")

        mail_hash = self.calculate_hash(data)
        self.save_file(mail_hash)


def calculate_hash(data) -> str:
    try:
        hash_module = hashlib.sha512()
        hash_module.update(data)
    except:
        logging.error("Error while hashing data!")
        raise custom_errors.HashingError

    return hash_module.hexdigest()


def return_mail():
    pass


def init_smtp():
    mail_server = EMAILServer()
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

    def need_manual_processing(self, filename):
        file_for_moving = self.config.email_path + filename
        if os.path.exists(file_for_moving) and os.path.isfile(file_for_moving) and os.path.exists(
                manual_dir) and os.path.isdir(manual_dir):
            try:
                shutil.move(file_for_moving, manual_dir + filename)
            except:
                raise Exception(SMTP.ERROR_MOVING,
                                "File doesn't exist or check if file is actually dir (moving problem)!")
        else:
            raise Exception(SMTP.ERROR_MOVING, "File doesn't exist or check if file is actually dir!")

        return SMTP.ERROR_OK

if __name__ == "__main__":
    config = config_loader.load_config()
    mail_config = MailConfigurations(config)
    loger_setup.init_logging(config)

    init_smtp()
