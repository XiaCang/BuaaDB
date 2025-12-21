import pymysql


DB_CONFIG = {
    'host': '124.70.86.207',
    'port': 3306,
    'user': 'u23371131',
    'password': 'Aa085277',
    'database': 'h_db23371131',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)