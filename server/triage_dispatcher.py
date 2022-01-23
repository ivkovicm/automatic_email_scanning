import pika
import os
from smtpd import SMTPServer
from user_modules import update_db
import asyncore
from eml_parser import EmlParser
import base64
from enum import Enum
import hashlib
import shutil
import threading
from other import config_loader, custom_types, custom_errors, rabbit_manipulation, loger_setup


class EMAILServer(SMTPServer):
    def __init__(self, config: dict):
        self.config = config
        self.email_path = ""
        self.manual_dir = ""
        self.local_ip = ""
        self.local_port = ""
        self.remote_ip = ""
        self.remote_port = ""
        self.parse_config()
        super(EMAILServer, self).__init__()

    def parse_config(self) -> None:
        self.email_path = self.config["SMTPServer"]["Eml_Path"]
        self.manual_dir = self.config["SMTPServer"]["Manual_Check"]
        self.local_ip = self.config["SMTPServer"]["Local_IP"]
        self.local_port = self.config["SMTPServer"]["Local_Port"]
        self.remote_ip = self.config["SMTPServer"]["Remote_IP"]
        self.remote_port = self.config["SMTPServer"]["Remote_Port"]
        self.check_config()

    def check_config(self) -> None:
        if self.local_port == "" or self.local_ip == "" or self.remote_port == "" or self.remote_ip == "":
            logging.critical("Error in configuration file (check SMTP IPs and PORTs)!")
            raise custom_errors.SMTPConfigError
        elif self.email_path == "" or self.manual_dir == "":
            logging.critical("Error in configuration file (check SMTP mails folder path)!")
            raise custom_errors.SMTPConfigError
        elif not os.path.isdir(self.email_path) or not os.path.isdir():
            logging.critical("SMTP directories for saving mails doesn't exist!")
            raise custom_errors.SMTPMailDirsError

    def need_manual_processing(self, filename):
        file_for_moving = self.email_path + filename
        if os.path.exists(file_for_moving) and os.path.isfile(file_for_moving) and os.path.exists(manual_dir) and os.path.isdir(manual_dir):
            try:
                shutil.move(file_for_moving, manual_dir + filename)
            except:
                raise Exception(SMTP.ERROR_MOVING, "File doesn't exist or check if file is actually dir (moving problem)!")
        else:
            raise Exception(SMTP.ERROR_MOVING, "File doesn't exist or check if file is actually dir!")

        return SMTP.ERROR_OK

    def parse_email(self):
        pass

    def process_message(self, peer, mailfrom, rcpttos, data, decode_data=False):
        global config

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
    global config



    mail_server = EMAILServer((local_ip, local_port), (remote_ip, remote_port))
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    config = config_loader.load_config()
    loger_setup.init_logging(config)

    init_smtp()

