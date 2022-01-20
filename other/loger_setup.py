import logging


def logging_level(argument):
    switcher = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return switcher.get(argument, logging.WARNING)


def init_logging(config) -> None:
    will_log = config["Logging"]["OnOff"]
    log_type = config["Logging"]["Type"]
    log_file = config["Logging"]["File"]
    log_level = logging_level(config["Logging"]["Level"])
    syslog_ip = config["Logging"]["SysLog_IP"]
    syslog_port = config["Logging"]["SysLog_PORT"]

    if will_log.lower() == "off" or not will_log:
        logging.basicConfig(filename="/dev/null", level=logging.CRITICAL)
    elif log_type.lower() == "file":
        if log_file != "":
            try:
                logging.basicConfig(filename=log_file, level=log_level, format='%(asctime)s : %(levelname)s : %(name)s : %(message)s')
            except:
                try:
                    logging.basicConfig(filename="/tmp/analysis_log.log", level=log_level,
                                        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', force=True)
                    print("Logging set to '/tmp/analysis_log.log'!")
                    logging.error("Error with logging to FILE: {}!".format(log_file))
                except:
                    logging.basicConfig(level=log_level, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', force=True)
                    logging.error("Error with logging to FILE: {} and FILE: {}!".format(log_file, "/tmp/analysis_log.log"))
        else:
            try:
                logging.basicConfig(filename="/tmp/analysis_log.log", level=log_level,
                                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', force=True)
                print("Logging set to '/tmp/analysis_log.log'!")
                logging.error("Error with logging to FILE: {}!".format(log_file))
            except:
                logging.basicConfig(level=log_level, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
                                    force=True)
                logging.error("Error with logging to FILE: {}!".format("/tmp/analysis_log.log"))
    elif log_type.lower() == "syslog":
        if syslog_ip == "":
            syslog_ip = "localhost"
        if syslog_port == "" or syslog_port == "0":
            syslog_port = 514
        try:
            logging.basicConfig.SysLogHandler(address=(syslog_ip, syslog_port))
            logging.Formatter(fmt='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        except:
            try:
                logging.basicConfig(filename="/tmp/analysis_log.log", level=log_level,
                                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', force=True)
                print("Logging set to '/tmp/analysis_log.log'!")
                logging.error("Error with logging to IP: {} on PORT: {}!".format(syslog_ip, syslog_port))
            except:
                logging.basicConfig(level=log_level, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
                                    force=True)
                print("Logging set to STDOUT!")
                logging.error("Error with logging to IP: {} on PORT: {} and to FILE: {}!".format(syslog_ip, syslog_port, "/tmp/analysis_log.log"))

