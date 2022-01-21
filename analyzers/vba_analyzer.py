import sys
import os
from oletools.olevba import VBA_Parser, TYPE_OLE
from oletools.olevba import ProcessingError, FileOpenError
from base64 import b64decode
import csv
import io
import magic
from time import sleep
import threading
from db_handling import update_db
from other import config_loader, custom_errors

packed_file_types = ["CDFV2 Encrypted"]
good_file_types = ["Composite Document File V2 Document"]


class VbaReport:
    def __init__(self, config, filename, payload):
        self.config = config

        self.file = ""
        self.filename= filename
        self.payload = payload

        self.malicious_count = 0
        self.suspicious_count = 0
        self.other_count = 0

        self.file_type = ""
        self.vbaparser = VBA_Parser
        self.vba_type = ""

        self.report = ""
        self.analysis_results = []
        self.verdict = None

        self.parse_config(config)
        self.save_payload_to_file()

    def parse_config(self, config) -> None:
        logging.debug("Parsing VBA values from configuration file!")
        temp_dir = config["AnalysisPlugins"]["VBA_Analyzer"]["temp_folder"]
        self.malicious_count = config["ID_Score"]["Malicious"]
        self.suspicious_count = config["ID_Score"]["Suspicious"]
        self.other_count = config["ID_Score"]["Other"]
        self.check_parsed_values(temp_dir)

    def check_parsed_values(self, temp) -> None:
        if self.malicious_count == "" or not self.malicious_count.isnumeric():
            self.malicious_count = 4
            logging.warning("Malicious count in configuration file is not a number!")
            logging.info("Malicious count set to 4!")
        if self.suspicious_count == "" or not self.suspicious_count.isnumeric():
            self.suspicious_count = 2
            logging.warning("Suspicious count in configuration file is not a number!")
            logging.info("Suspicious count set to 2!")
        if self.other_count == "" or not self.other_count.isnumeric():
            self.other_count = 0
            logging.warning("Other count in configuration file is not a number!")
            logging.info("Other count set to 0!")
        if temp == "" or not os.path.isdir():
            logging.warning("Temporary directory not set in configuration file or doesn't exist!")
            logging.info("Temporary directory set to '/tmp/'!")
            self.file = "/tmp/" + self.filename
        else:
            self.file = temp + self.filename

    def save_payload_to_file(self):
        self.file = self.temp_dir + self.filename
        try:
            with open(self.file, "wb") as fh:
                fh.write(self.payload)
                fh.close()
        except:
            logger.error("Error while saving payload to file {}!".format(self.file))
            raise custom_errors.VBASaveToFile

    def init_parsing(self) -> None:
        try:
            self.vbaparser = VBA_Parser(self.file)
        except FileOpenError:
            logging.error("Error while opening file {} with VBA_Parser!".format(self.file))
            raise custom_errors.VBAParsing
        except ProcessingError:
            logging.error("Error while processing file {} with VBA_Parser!".format(self.file))
            raise custom_errors.VBAParsing
        except:
            logging.error("Error while working on file {} with VBA_Parser!".format(self.file))
            raise custom_errors.VBAParsing

    def detect_macro(self) -> None:
        try:
            test = self.vbaparser.detect_vba_macros()
        except:
            logger.error("Error while detecting macro, file {}!".format(self.file))
            raise custom_errors.VBADetectMacro

        if test:
            self.vba_type &= custom_types.VBA_MACRO.VBA_HAS_MACRO.value
        elif not test and self.vbaparser.type == TYPE_OLE:
            self.vba_macro_flags &= VBASTATUS.STATUS_VBA_POSSIBLE_FALSE_NEGATIVE.value
        else:
            self.vba_macro_flags &= VBASTATUS.STATUS_VBA_MACRO_NOT_FOUND.value

    def analyse_macro(self) -> None:
        try:
            self.analysis_results = self.vbaparser.analyze_macros(show_decoded_strings=True, deobfuscate=True)
        except:
            logger.error("Error while analysing macro, file {}!".format(self.file))
            raise custom_errors.VBAAnalysisError

    def create_report(self) -> None:
        try:
            self.report = [["Type", "Keyword", "Description"]]
            for kw_type, keyword, description in self.analysis_results:
                self.report.append([])
                self.report[len(self.report) - 1].append(kw_type)
                self.report[len(self.report) - 1].append(keyword)
                self.report[len(self.report) - 1].append(description)
        except:
            logger.error("Error while creating report, file {}!".format(self.file))
            raise custom_errors.VBACreateReport

    def save_report_to_disk(self) -> None:
        report_to_save = csv_worker.string_to_csv(self.report)
        try:
            with open("/reports/" + self.filename, "w", encoding="UTF-8") as fh:
                fh.write(report_to_save)
        except:
            logging.error("Error while saving report for file {} to disk!".format(self.filename))
            raise custom_errors.VBASaveToDisk

    def write_to_db(self) -> None:
        try:
            connection = update_db.ConnectionObject(self.config)
            connection.create_row_in_db(self.filename, self.file_type, self.verdict)
        except:
            logger.error("Error while saving verdict to DB!")

    def calculate_verdict(self) -> None:
        try:
            susp_cnt = 0
            other_cnt = 0
            evil = False
            for row in self.report:
                if row[0] == "Dridex String":
                    evil = True
                    break
                elif row[0] == "Suspicious":
                    susp_cnt += 1
                elif row[0] == "AutoExec":
                    other_cnt += 1

            if evil:
                self.verdict = custom_types.VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= self.malicious_count:
                self.verdict = custom_types.VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= self.suspicious_count and other_cnt >= self.other_count:
                self.verdict = custom_types.VERDICT.VERDICT_MALICIOUS
            elif susp_cnt >= self.suspicious_count:
                self.verdict = custom_types.VERDICT.VERDICT_SUSPICIOUS
            else:
                self.verdict = custom_types.VERDICT.VERDICT_GOODWARE
        except:
            self.verdict = custom_types.VERDICT.MANUAL
            logger.warning("Error while giving verdict to file {}!".format(self.file))
            raise VBAVerdictError(self.filename)

    def get_verdict(self) -> custom_types.VERDICT:
        return self.verdict.name
