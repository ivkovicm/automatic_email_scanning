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
