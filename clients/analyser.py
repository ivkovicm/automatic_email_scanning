import sys
import os
from analyzers import vba_analayzer
from other import config_loader, custom_errors, custom_types


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


def main() -> None:
    pass


if __name__ == '__main__':
    # Parsing configuration file
    config = config_loader.load_config()
    # Setting up logger
    loger_setup.init_logging(config)
    # Checking which analysis plugins are ON
    ANALYSIS = 0
    for analysis in config["AnalysisPlugins"]:
        if analysis["On_Off"].lower() == "on":
            if analysis["Plugin"] == "VBA":
                ANALYSIS &= Analysis.VBA
            elif analysis["Plugin"] == "AV":
                ANALYSIS &= Analysis.AV
            elif analysis["Plugin"] == "EMAIL":
                ANALYSIS &= Analysis.EMAIL
    # If no analysis plugins are ON log and exit
    if ANALYSIS == Analysis.NONE:
        loggin.critical("All analysis plugins are off, check your configuration file!")
        sys.exit(1)
    # If analysis is ON check which it is and log
    else:
        if ANALYSIS & Analysis.VBA:
            logging.info("Files will be checked for macro!")
        if ANALYSIS & ANALYSIS.AV:
            logging.info("Files will be checked with AV!")
        if ANALYSIS & Analysis.EMAIL:
            logging.info("Emails will be parsed!")

    try:
        main()
    except KeyboardInterrupt:
        print('Manually interrupted!')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
