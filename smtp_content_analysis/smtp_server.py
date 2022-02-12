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


class EmailReceiver(SMTPServer):
    def __init__(self, config: dict):
        self.mail_config = mail_config
        self.rabbit_config = rabbit_manipulation.RabbitConfig(config)
        super(EMAILServer, self).__init__((self.mail_config.ingress_ip, self.mail_config.ingress_port), None)

    def process_message(self, peer, mailfrom, rcpttos, data, decode_data=False):

        mailfrom.replace("\'", "")
        mailfrom.replace("\"", "")

        for recipient in rcpttos:
            recipient.replace("\'", "")
            recipient.replace("\'", "")

        mail_hash = self.calculate_hash(data)
        file_handling.save_file(self.config.email_path + mail_hash)


def calculate_hash(data) -> str:
    try:
        hash_module = hashlib.sha512()
        hash_module.update(data)
    except:
        logging.error("Error while hashing data!")
        raise custom_errors.HashingError

    return hash_module.hexdigest()


def main(config: dict):
    mail_server = EMAILServer(config)
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
    loger_setup.init_logging(config)
    mail_config = custom_types.MailConfigurations(config)
    main()
