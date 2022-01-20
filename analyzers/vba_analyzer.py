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
from time import sleep
import threading
from db_handling import update_db
from other import config_loader


packed_file_types = ["CDFV2 Encrypted"]
good_file_types = ["Composite Document File V2 Document"]


class VbaReport:
    def __init__(self, config):
        self.temp_dir = ""
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

    def init_temp(self, config):
        self.temp_dir = config["AnalysisPlugins"]["VBA_Analyzer"]["temp_folder"]
        if self.temp_dir == "":
            self.temp_dir = "/tmp/"




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
                self.vba_flags &= VBASTATUS.STATUS_PACKED.value
            elif self.file_type in good_file_types:
                self.vba_flags &= VBASTATUS.STATUS_OK.value
            else:
                self.vba_flags &= VBASTATUS.STATUS_WRONG_FORMAT.value
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
            self.vba_macro_flags &= VBASTATUS.STATUS_VBA_POSSIBLE_FALSE_NEGATIVE.value
        else:
            self.vba_macro_flags &= VBASTATUS.STATUS_VBA_MACRO_NOT_FOUND.value

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

