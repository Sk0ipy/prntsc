import mysql.connector

# connect to the database
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="prntsc_db_pool",
    pool_size=5,
    host="localhost",
    user="root",
    database="prntsc_db"
)

# get all the working urls from the database
with connection_pool.get_connection() as connection, connection.cursor() as cursor:
    cursor.execute("SELECT url FROM working_urls")
    urls = cursor.fetchall()

    for url in urls:
        print(url[0])
