import yaml
import os
import sys
from other import loger_setup, custom_errors


def load_config(path_to_config="./configs/config.json") -> dict:
    try:
        with open(path_to_config, "r") as fh:
            config = yaml.load(fh, Loader=yaml.FullLoader)
    except OSError:
        print("CRITICAL error while opening configuration file!")
        sys.exit(1)

    return config


class SMTPServerConfigurations:
    def __init__(self, config: dict):
        self.email_path = ""
        self.ingress_port = ""
        self.ingress_ip = ""
        self.parse_config(config)

    def parse_config(self, config) -> None:
        self.email_path = config["SMTPServer"]["Eml_Path"]
        self.ingress_port = config["SMTPServer"]["Ingress_Port"]
        self.ingress_ip = config["SMTPServer"]["Ingress_IP"]
        self.check_config()

    def check_config(self) -> None:
        if self.ingress_port == "" or self.ingress_ip == "":
            logging.critical("Error in configuration file (check Ingress SMTP IPs and PORTs)!")
            raise custom_errors.SMTPConfigError
        elif self.email_path == "":
            logging.critical("Error in configuration file (check Ingress SMTP mails folder path)!")
            raise custom_errors.SMTPConfigError
        elif not os.path.isdir(self.email_path):
            logging.critical("SMTP directories for saving mails doesn't exist!")
            raise custom_errors.SMTPMailDirsError


class SMTPClientConfiguration:
    def __init__(self, config: dict):
        self.email_path = ""
        self.manual_path = ""
        self.quarantine_path = ""
        self.egress_port = ""
        self.egress_ip = ""
        self.parse_config(config)

    def parse_config(self, config) -> None:
        self.email_path = config["SMTPClient"]["Eml_Path"]
        self.manual_path = config["SMTPClient"]["Manual_Path"]
        self.quarantine_path = config["SMTPClient"]["Quarantine_Path"]
        self.egress_port = config["SMTPClient"]["Egress_Port"]
        self.egress_ip = config["SMTPClient"]["Egress_IP"]
        self.check_config()

    def check_config(self) -> None:
        if self.egress_port == "" or self.egress_ip == "":
            logging.critical("Error in configuration file (check Egress SMTP IPs and PORTs)!")
            raise custom_errors.SMTPConfigError
        elif self.email_path == "" or self.manual_path == "" or self.quarantine_path == "":
            logging.critical("Error in configuration file (check Egress SMTP mails folder path)!")
            raise custom_errors.SMTPConfigError
        elif not os.path.isdir(self.email_path) or not os.path.isdir(self.manual_path) or not os.path.isdir(self.quarantine_path):
            logging.critical("SMTP directories for saving mails doesn't exist!")
            raise custom_errors.SMTPMailDirsError


class RabbitConfiguration:
    def __init__(self, config: dict):
        self.hostname = ""
        self.port = ""
        self.analysis_queue = ""
        self.manual_queue = ""
        self.error_queue = ""
        self.verdict_queue = ""
        self.parse_config(config)

    def parse_config(self, config: dict) -> None:
        self.hostname = config["RabbitMQ"]["Hostname"]
        self.port = config["RabbitMQ"]["Port"]
        self.analysis_queue = config["RabbitMQ"]["Queue"]["Analysis"]
        self.manual_queue = config["RabbitMQ"]["Queue"]["Manual"]
        self.error_queue = config["RabbitMQ"]["Queue"]["Error"]
        self.verdict_queue = config["RabbitMq"]["Queue"]["Error"]
        self.check_config()

    def check_config(self) -> None:
        if self.hostname == "" or self.analysis_queue == "" or self.manual_queue == "" or self.error_queue == "" or self.verdict_queue == "":
            logging.critical("Error while parsing configuration file (RabbitMQ config)!")
            raise custom_errors.ConfigurationNotSet
