import pymysql

database_config = {
    "host": "localhost",
    "user": "root",
    "passwd": "root",
    "db": "bd50_1_18_matveeva_sm",
    "port": 8889
}

db = pymysql.connect(host=database_config['host'], user=database_config['user'],
                     passwd=database_config['passwd'], db=database_config['db'], port=database_config['port'])

    telegram_key = 'YOUR_KEY'
