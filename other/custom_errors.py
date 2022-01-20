# DB errors

class PostgreSQLconnectionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__("PostgreSQL ERROR while " + str(message))


class ConfigurationNotSet(Exception):
    def __init__(self):
        super().__init__("Check if your DataBase configuration is set in configs/config.json!")


class MessageParsingError(Exception):
    def __init__(self, filename):
        super().__init__("Error with message {}!".format(filename))


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