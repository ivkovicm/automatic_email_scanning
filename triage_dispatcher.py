import pika
import os
from smtpd import SMTPServer
from user_modules import update_db
import asyncore
from eml_parser import EmlParser
import base64
from enum import Enum
import hashlib
import yaml
import shutil
import threading

with open("./configs/config.json", "r") as fh:
    config = yaml.load(fh, Loader=yaml.FullLoader)

class SMTP(Enum):
    ERROR_OK = 0
    ERROR_ERROR = 1
    ERROR_HASHING = 2
    ERROR_DELETING = 3
    ERROR_SAVING = 4
    ERROR_MOVING = 5

class EMAILServer(SMTPServer):
    @staticmethod
    def calculate_hash(data):
        try:
            hash_module = hashlib.sha512()
            hash_module.update(data)
        except:
            raise Exception(SMTP.ERROR_HASHING, "Error while calculating HASH!")

        return hash_module.hexdigest()

    @staticmethod
    def rm_file(file_for_cleaning):
        if os.path.exists(file_for_cleaning) and os.path.isfile(file_for_cleaning):
            os.remove(file_for_cleaning)
        else:
            raise Exception(SMTP.ERROR_DELETING, "File doesn't exist or chek if file is actually dir!")

        return SMTP.ERROR_OK

    @staticmethod
    def save_file(filename):
        global config

        email_path = config["SMTPServer"]["Eml_Path"]
        try:
            with open(email_path + filename, "w") as fh:
                fh.write()
        except:
            raise Exception(SMTP.ERROR_SAVING, "Error while saving email!")

        return SMTP.ERROR_OK

    @staticmethod
    def need_manual_processing(filename):
        global config

        email_path = config["SMTPServer"]["Eml_Path"]
        manual_dir = config["SMTPServer"]["Manual_Check"]
        file_for_moving = email_path + filename
        if os.path.exists(file_for_moving) and os.path.isfile(file_for_moving) and os.path.exists(manual_dir) and os.path.isdir(manual_dir):
            try:
                shutil.move(file_for_moving, manual_dir + filename)
            except:
                raise Exception(SMTP.ERROR_MOVING, "File doesn't exist or check if file is actually dir (moving problem)!")
        else:
            raise Exception(SMTP.ERROR_MOVING, "File doesn't exist or check if file is actually dir!")

        return SMTP.ERROR_OK

    def parse_email

    def process_message(self, peer, mailfrom, rcpttos, data, decode_data=False):
        global config

        mailfrom.replace("\'", "")
        mailfrom.replace("\"", "")

        for recipient in rcpttos:
            recipient.replace("\'", "")
            recipient.replace("\'", "")

        mail_hash = self.calculate_hash(data)
        self.save_file(mail_hash)


def send_to_analysis(mssg):
    global config
    mq_hostname = config["RabbitMQ"]["Hostname"]
    mq_port = config["RabbitMQ"]["Port"]
    mq_queue = config["RabbitMQ"]["Queue"]["Analysis"]
    if mq_queue != 0:
        connection = pika.BlockingConnection(pika.ConnectionParameters(mq_hostname, mq_port))
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters(mq_hostname))

    channel = connection.channel()
    channel.queue_declare(queue=mq_queue)
    channel.basic_publish(exchange='', routing_key=mq_queue, body=mssg)

    connection.close()

def return_mail():
    pass

def init_smtp():
    global config

    local_ip = config["SMTPServer"]["Local_IP"]
    local_port = config["SMTPServer"]["Local_Port"]
    remote_ip = config["SMTPServer"]["Remote_IP"]
    remote_port = config["SMTPServer"]["Remote_Port"]

    mail_server = EMAILServer((local_ip, local_port), (remote_ip, remote_port))
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    init_smtp()

