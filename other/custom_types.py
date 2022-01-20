class SQL(Enum):
    SQL_NO_ENTRY = 0
    SQL_EXISTS = 1
    SQL_STRANGE_RECORDS = 2
    SQL_ENTRY_MALICIOUS = 3
    SQL_ENTRY_SUSPICIOUS = 4
    SQL_ENTRY_GOODWARE = 5
    SQL_ERROR_CONNECTION_TYPE = 6
    SQL_ERROR_NO_CONNECTION = 7
    SQL_OK = 8


class VBA_STATUS(Enum):
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


# Used in analyser for determination what will be attachment be checked for
class Analysis(Enum):
    NONE = 0
    VBA = 1 << 0
    AV = 1 << 1
    EMAIL = 1 << 2
