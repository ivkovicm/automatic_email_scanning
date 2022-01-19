import pika
import sys
import os
from enum import Enum
from oletools.olevba import VBA_Parser, TYPE_OLE
from oletools.olevba import ProcessingError, FileOpenError
from base64 import b64decode
import csv
import io
import magic
import yaml
from time import sleep
import threading
from user_modules import update_db


packed_file_types = ["CDFV2 Encrypted"]
good_file_types = ["Composite Document File V2 Document"]

with open("./configs/config.json", "r") as fh:
    config = yaml.load(fh, Loader=yaml.FullLoader)

PATH_TO_TEMP = "/tmp/"


class VbaReport:
    def __init__(self):
        self.temp_dir = PATH_TO_TEMP
        self.FILE_PATH = ""
        self.filename = ""
        self.payload = None
        self.file_type = ""
        self.vbaparser = VBA_Parser
        self.vba_flags = 0
        self.error_flags = 0
        self.vba_macro_flags = 0
        self.manual_check = False
        self.suspicious_counter = 0
        self.MALWARE = False
        self.SUSPICIOUS = False
        self.report = ""
        self.analysis_results = []
        self.verdict = VERDICT

    def parse_body(self, body):
        try:
            print(type(body))
            body_arguments = body.decode("UTF-8").split("|")
            self.filename = body_arguments[0]
            self.payload = b64decode(body_arguments[1].encode())
        except:
            self.error_flags &= ERROR.ERROR_BODY_PARSING.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def save_to_file(self):
        self.FILE_PATH = self.temp_dir + self.filename
        try:
            with open(self.FILE_PATH, "wb") as fh:
                fh.write(self.payload)
                fh.close()
        except:
            self.error_flags &= ERROR.ERROR_FILE_SAVING.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def check_file_magic(self):
        try:
            with magic.Magic() as majik:
                self.file_type = majik.id_filename(self.FILE_PATH)
            print("[x] File type: " + self.file_type)
            if self.file_type in packed_file_types:
                self.vba_flags &= STATUS.STATUS_PACKED.value
            elif self.file_type in good_file_types:
                self.vba_flags &= STATUS.STATUS_OK.value
            else:
                self.vba_flags &= STATUS.STATUS_WRONG_FORMAT.value
        except:
            self.error_flags &= ERROR.ERROR_FILE_MAGIC.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def init_parsing(self):
        try:
            self.vbaparser = VBA_Parser(self.FILE_PATH)
        except FileOpenError:
            self.error_flags &= ERROR.ERROR_OPEN_VBA.value
            return ERROR.ERROR_ERROR
        except ProcessingError:
            self.error_flags &= ERROR.ERROR_PROCESSING_VBA.value
            return ERROR.ERROR_ERROR
        except:
            self.error_flags &= ERROR.ERROR_PARSING_VBA.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def detect_macro(self):
        try:
            test = self.vbaparser.detect_vba_macros()
        except:
            self.error_flags &= ERROR.ERROR_DETECTING_MACRO.value
            return ERROR.ERROR_ERROR

        if test:
            self.vba_macro_flags &= VBA_MACRO.VBA_HAS_MACRO.value
        elif not test and self.vbaparser.type == TYPE_OLE:
            self.vba_macro_flags &= STATUS.STATUS_VBA_POSSIBLE_FALSE_NEGATIVE.value
        else:
            self.vba_macro_flags &= STATUS.STATUS_VBA_MACRO_NOT_FOUND.value

        return ERROR.ERROR_OK

    def analyse_macro(self):
        try:
            self.analysis_results = self.vbaparser.analyze_macros(show_decoded_strings=True, deobfuscate=True)
        except:
            self.error_flags &= ERROR.ERROR_ANALYSING_MACRO.value
            return ERROR.ERROR_ERROR

        try:
            self.report = [["Type", "Keyword", "Description"]]
            for kw_type, keyword, description in self.analysis_results:
                self.report.append([])
                self.report[len(self.report) - 1].append(kw_type)
                self.report[len(self.report) - 1].append(keyword)
                self.report[len(self.report) - 1].append(description)
                print(kw_type + "\t" + keyword + "\t" + description)
        except:
            self.error_flags &= ERROR.ERROR_PREPARING_REPORT.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def report_to_csv_string(self):
        try:
            with io.StringIO() as output:
                csv_writer = csv.writer(output)
                csv_writer.writerows(self.report)
                self.report = output.read()
        except:
            self.error_flags &= ERROR.ERROR.ERROR_TRANSFORMING_REPORT.value
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def write_to_db(self):
        try:
            update_db.create_row_in_db(config, self.filename, self.file_type, self.verdict)
        except:
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def calculate_verdict(self):
        global config
        try:
            susp_cnt = 0
            other_cnt = 0
            evil = False
            for row in self.report:
                if row[0] == "Dridex String":
                    evil = True
                elif row[0] == "Suspicious":
                    susp_cnt += 1
                elif row[0] == "AutoExec":
                    other_cnt += 1

            if evil:
                self.verdict = VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= config["ID_Score"]["Malicious"]:
                self.verdict = VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= config["ID_Score"]["Suspicious"] and other_cnt >= config["ID_Score"]["Other"]:
                self.verdict = VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= config["ID_Score"]["Suspicious"]:
                self.verdict = VERDICT.VERDICT_SUSPICIOUS
            else:
                self.verdict = VERDICT.VERDICT_GOODWARE
        except:
            return ERROR.ERROR_ERROR

        return ERROR.ERROR_OK

    def get_verdict(self):
        return self.verdict.name


class STATUS(Enum):
    STATUS_OK = 0
    STATUS_WRONG_FORMAT = 1 << 0
    STATUS_VBA_PARSING_ERROR = 1 << 1
    STATUS_VBA_MACRO_FOUND = 1 << 2
    STATUS_VBA_MACRO_NOT_FOUND = 1 << 3
    # For some formats (as PowerPoint97-2003) detect_vba_macros will always return False
    # Macros are stored in different way
    STATUS_VBA_POSSIBLE_FALSE_NEGATIVE = 1 << 4
    STATUS_PACKED = 1 << 5
    STATUS_MALICIOUS = 1 << 6
    STATUS_SUSPICIOUS = 1 << 7
    STATUS_GOOD = 1 << 8
    STATUS_NEED_MANUAL_CHECKING = 1 << 9


class VERDICT(Enum):
    GOODWARE = 0
    SUSPICIOUS = 1
    MALICIOUS = 2
    MANUAL = 666


class VBA_MACRO(Enum):
    VBA_NO_MACRO = 0
    VBA_HAS_MACRO = 1 << 0
    VBA_POSSIBLE_MACRO = 1 << 1


class ERROR(Enum):
    ERROR_OK = 0
    ERROR_ERROR = -1
    ERROR_BODY_PARSING = 1 << 0
    ERROR_FILE_SAVING = 1 << 1
    ERROR_FILE_MAGIC = 1 << 2
    ERROR_OPEN_VBA = 1 << 3
    ERROR_PROCESSING_VBA = 1 << 4
    ERROR_PARSING_VBA = 1 << 5
    ERROR_DETECTING_MACRO = 1 << 6
    ERROR_ANALYSING_MACRO = 1 << 7
    ERROR_PREPARING_REPORT = 1 << 8
    ERROR_TRANSFORMING_REPORT = 1 << 9


def need_manual_checking(body: str):
    global config

    mq_hostname = config["RabbitMQ"]["Hostname"]
    mq_port = config["RabbitMQ"]["Port"]
    mq_queue = config["RabbitMQ"]["Queue"]["Manual"]

    try:
        if mq_queue != 0:
            connection = pika.BlockingConnection(pika.ConnectionParameters(mq_hostname, mq_port))
        else:
            connection = pika.BlockingConnection(pika.ConnectionParameters(mq_hostname))

        channel = connection.channel()
        channel.queue_declare(queue=mq_queue)
        channel.basic_publish(exchange='', routing_key=mq_queue, body=body)
        connection.close()
    except:
        return -1

    return 0


def threading_analysis(body: str):
    test = VbaReport()
    flag = test.parse_body(body)
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1
    flag = test.save_to_file()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1
    flag = test.check_file_magic()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1
    flag = test.init_parsing()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1

    flag = test.detect_macro()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1

    flag = test.analyse_macro()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1

    flag = test.report_to_csv_string()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1

    flag = test.calculate_verdict()
    if flag == ERROR.ERROR_ERROR:
        need_manual_checking(body)
        return -1

    return 0


def callback(ch, method, properties, body):
    th = threading.Thread(target=threading_analysis(body))
    th.start()
    sleep(0.1)


def main():
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

    channel.basic_consume(queue=mq_queue, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
