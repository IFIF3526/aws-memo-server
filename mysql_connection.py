import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'yh-db.cztqqfotbirp.ap-northeast-2.rds.amazonaws.com',
        database = 'memo_app_db',
        user = 'memo_user',
        password= 'memo1234'
    )
    return connection