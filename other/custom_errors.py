# DB errors

class PostgreSQLconnectionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__("PostgreSQL ERROR while " + str(message))


class ConfigurationNotSet(Exception):
    pass


class MessageParsingError(Exception):
    def __init__(self, filename):
        super().__init__("Error with message {}!".format(filename))


class MessageNotPrepared(Exception):
    pass


# VBA Analysis plug-in errors
class VBAVerdictError(Exception):
    def __init__(self, filename):
        super().__init__("Error while giving verdict to file {}!".format(filename))


class VBAAnalysisError(Exception):
    pass


class VBACreateReport(Exception):
    pass


class VBADetectMacro(Exception):
    pass


class VBASaveToFile(Exception):
    pass


class VBAParsing(Exception):
    pass


class VBASaveToDisk(Exception):
    pass


# Errors for other files
class ConvertToCSVError(Exception):
    pass


# Errors for SMTP
class HashingError(Exception):
    pass


class SMTPConfigError(Exception):
    pass


class SMTPMailDirsError(Exception):
    pass


class SMTP(Enum):
    ERROR_OK = 0
    ERROR_ERROR = 1
    ERROR_HASHING = 2
    ERROR_DELETING = 3
    ERROR_SAVING = 4
    ERROR_MOVING = 5
