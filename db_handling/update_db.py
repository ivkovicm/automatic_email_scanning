import psycopg2
from other import custom_errors, custom_types


class ConnectionObject:
    def __init__(self, config):
        self.db_type = config["DataBase"]["Type"]
        self.db_host = config["DataBase"]["Hostname"]
        self.db_port = config["DataBase"]["Port"]
        self.db_name = config["DataBase"]["DB_name"]
        self.db_user = config["DataBase"]["User"]
        self.db_password = config["DataBase"]["Password"]
        self.dsn = ""
        self.conn_object = None
        self.init_connection()

        self.check_if_all_entries_populated()
        self.set_dsn()

    def check_if_all_entries_populated(self) -> None:
        if self.db_host == "" or self.db_name == "" or self.db_user == "" or self.db_password == "" or self.db_user == "" or self.db_password == "":
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

    @staticmethod
    def verdict_field_to_enum(argument) -> custom_types.SQL:
        switcher = {
            "MALICIOUS": custom_types.SQL.SQL_ENTRY_MALICIOUS,
            "SUSPICIOUS": custom_types.SQL.SQL_ENTRY_SUSPICIOUS,
            "GOODWARE": custom_types.SQL.SQL_ENTRY_GOODWARE,
        }
        return switcher.get(argument, custom_types.SQL.SQL_STRANGE_RECORDS)

    def init_connection(self) -> None:
        if self.db_type == "psql":
            self.connect_to_db()
        else:
            raise ConfigurationNotSet

    def close_connection(self) -> None:
        if self.db_type == "psql":
            try:
                self.conn_object.close()
            except:
                raise PostgreSQLconnectionError(
                    "closing connection to" + str(self.conn_object.db_host) + ":" + str(self.conn_object.db_port))
        else:
            pass

    def connect_to_db(self) -> None:
        if self.db_type == "psql":
            try:
                self.conn_object = psycopg2.connect(self.dsn)
            except:
                raise PostgreSQLconnectionError("connecting to" + str(self.conn_object.db_host) + ":" + str(self.conn_object.db_port))
        else:
            pass

    def fetch_verdict(self, your_hash: str) -> custom_types.SQL:
        self.init_connection()
        query_sql = 'SELECT SHA512, VERDICT from ' + self.db_name + ' where SHA512=="' + your_hash + '"'
        cur = self.conn_object.cursor()
        cur.execute(query_sql)
        if len(cur) == 0:
            cur.close()
            self.close_connection()
            return custom_types.SQL.SQL_NO_ENTRY
        elif len(cur) != 1:
            cur.close()
            self.close_connection()
            return SQL.SQL_STRANGE_RECORDS
        else:
            cur.close()
            self.close_connection()
            return verdict_field_to_enum(cur[1])

    def update_db_entry(self, your_hash: str, verdict: str) -> None:
        self.init_connection()
        update_sql = 'UPDATE ' + self.db_name + 'SET counter = counter + 1 and SET verdict =' + verdict + ' where SHA512=="' + your_hash
        cur = self.conn_object.cursor()
        cur.execute(update_sql)
        self.conn_object.commit()
        cur.close()
        self.close_connection()

    def create_row_in_db(self, your_hash: str, file_type: str, verdict: str) -> None:
        self.init_connection()
        create_sql = "INSERT INTO " + self.db_name + "(HASH512,FILE_TYPE,COUNTER,VERDICT) VALUES('" + your_hash + "','" + file_type + "'," + str(
            1) + ",'" + verdict + "'"
        cur = self.conn_object.cursor()
        cur.execute(create_sql)
        self.conn_object.commit()
        cur.close()
        self.close_connection()
