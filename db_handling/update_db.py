import psycopg2
from enum import Enum
from other import custom_errors, custom_types

conn_object = None


class ConnectionObject:
    def __init__(self, config):
        self.db_host = config["DataBase"]["Hostname"]
        self.db_port = config["DataBase"]["Port"]
        self.db_name = config["DataBase"]["DB_name"]
        self.db_user = config["DataBase"]["User"]
        self.db_password = config["DataBase"]["Password"]
        self.dsn = ""
        self.object = psycopg2.connection
        self.check_if_all_entries_populated()
        self.set_dsn()

    def check_if_all_entries_populated(self) -> None:
        if self.db_host == "" or self.db_name == "" or self.db_user == "" or self.db_password == "":
            raise ConfigurationNotSet
        elif self.db_port == "":
            self.db_port = 0

    def set_dsn(self) -> None:
        if self.db_port == 0:
            self.dsn = "host={} dbname={} user={} password={}".format(self.db_host, self.db_name, self.db_user,
                                                                      self.db_password)
        else:
            self.dsn = "host={} port={} dbname={} user={} password={}".format(self.db_host, self.db_port, self.db_name,
                                                                              self.db_user, self.db_password)


def verdict_field_to_enum(argument) -> SQL:
    switcher = {
        "MALICIOUS": SQL.SQL_ENTRY_MALICIOUS,
        "SUSPICIOUS": SQL.SQL_ENTRY_SUSPICIOUS,
        "GOODWARE": SQL.SQL_ENTRY_GOODWARE,
    }
    return switcher.get(argument, SQL.SQL_STRANGE_RECORDS)


def init_connection(config) -> SQL:
    if config["DataBase"]["Type"] == "psql":
        connect_to_db(config)
    else:
        raise ConfigurationNotSet

    return SQL.SQL_OK


def connect_to_db(config) -> SQL:
    global conn_object
    conn_object = ConnectionObject(config)
    try:
        conn_object = psycopg2.connect(conn_object.dsn)
    except:
        raise PostgreSQLconnectionError("connecting to" + str(conn_object.db_host) + ":" + str(conn_object.db_port))

    return SQL.SQL_OK


def fetch_verdict(config, your_hash: str) -> SQL:
    global conn_object
    init_connection(config)
    db_name = config["DataBase"]["DB_name"]
    query_sql = 'SELECT SHA512, VERDICT from ' + db_name + ' where SHA512=="' + your_hash + '"'
    cur = conn_object.cursor()
    cur.execute(query_sql)
    if len(cur) == 0:
        cur.close()
        conn_object.close()
        return SQL.SQL_NO_ENTRY
    elif len(cur) != 1:
        cur.close()
        conn_object.close()
        return SQL.SQL_STRANGE_RECORDS
    else:
        cur.close()
        conn_object.close()
        return verdict_field_to_enum(cur[1])


def update_db_entry(config, your_hash: str, verdict: str) -> None:
    global conn_object
    init_connection(config)
    db_name = config["DataBase"]["DB_name"]
    update_sql = 'UPDATE ' + db_name + 'SET counter = counter + 1 and SET verdict =' + verdict + ' where SHA512=="' + your_hash
    cur = conn_object.cursor()
    cur.execute(update_sql)
    conn_object.commit()
    cur.close()
    conn_object.close()


def create_row_in_db(config, your_hash: str, file_type: str, verdict: str) -> None:
    global conn_object
    init_connection(config)
    db_name = config["DataBase"]["DB_name"]
    create_sql = "INSERT INTO " + db_name + "(HASH512,FILE_TYPE,COUNTER,VERDICT) VALUES('" + your_hash + "','" + file_type + "'," + str(
        1) + ",'" + verdict + "'"
    cur = conn_object.cursor()
    cur.execute(create_sql)
    conn_object.commit()
    cur.close()
    conn_object.close()
