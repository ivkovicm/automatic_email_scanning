import psycopg2
from enum import Enum

conn_object = psycopg2.connection


def verdict_field_to_enum(argument):
    switcher = {
        "MALICIOUS": SQL.SQL_ENTRY_MALICIOUS,
        "SUSPICIOSU": SQL.SQL_ENTRY_SUSPICIOSU,
        "GOODWARE": SQL.SQL_ENTRY_GOODWARE,
    }
    return switcher.get(argument, SQL.SQL_STRANGE_RECORDS)


class SQL(Enum):
    SQL_NO_ENTRY = 0
    SQL_EXISTS = 1
    SQL_STRANGE_RECORDS = 2
    SQL_ENTRY_MALICIOUS = 3
    SQL_ENTRY_SUSPICIOSU = 4
    SQL_ENTRY_GOODWARE = 5
    SQL_ERROR_CONNECTION_TYPE = 6
    SQL_ERROR_NO_CONNECTION = 7
    SQL_OK = 8


def init_connection(config):
    if config["DataBase"]["Type"] == "sql":
        connect_to_db(config)
    else:
        raise Exception(SQL.SQL_ERROR_CONNECTION_TYPE, "Didn't find connection type!")
    return SQL.SQL_OK


def connect_to_db(config):
    global conn_object
    db_host = config["DataBase"]["Hostname"]
    db_port = config["DataBase"]["Port"]
    db_name = config["DataBase"]["DB_name"]
    db_user = config["DataBase"]["User"]
    db_password = config["DataBase"]["Password"]
    if db_port == 0:
        dsn = "host={} dbname={} user={} password={}".format(db_host, db_name, db_user, db_password)
    else:
        dsn = "host={} port={} dbname={} user={} password={}".format(db_host, db_port, db_name, db_user, db_password)
    try:
        conn_object = psycopg2.connect(dsn)
    except:
        raise Exception(SQL.SQL_ERROR_NO_CONNECTION, "Can't connect to DB")
    return SQL.SQL_OK


def fetch_verdict(config, your_hash: str):
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


def update_db_entry(config, your_hash: str, verdict: str):
    global conn_object
    init_connection(config)
    db_name = config["DataBase"]["DB_name"]
    update_sql = 'UPDATE ' + db_name + 'SET counter = counter + 1 and SET verdict =' + verdict + ' where SHA512=="' + your_hash
    cur = conn_object.cursor()
    cur.execute(update_sql)
    conn_object.commit()
    cur.close()
    conn_object.close()


def create_row_in_db(config, your_hash: str, file_type: str, verdict: str):
    global conn_object
    init_connection(config)
    db_name = config["DataBase"]["DB_name"]
    create_sql = "INSERT INTO " + db_name + "(HASH512,FILE_TYPE,COUNTER,VERDICT) VALUES('" + your_hash + "','" + file_type + "'," + str(1) + ",'" + verdict + "'"
    cur = conn_object.cursor()
    cur.execute(create_sql)
    conn_object.commit()
    cur.close()
    conn_object.close()
