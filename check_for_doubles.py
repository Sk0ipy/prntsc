import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="prntsc_db"
)


# database name to check is urls


def main():
    cursor = mydb.cursor()
    sql_query = "SELECT url, count(*) as count FROM urls GROUP BY url HAVING count(*) > 1"
    cursor.execute(sql_query)
    result = cursor.fetchall()
    mydb.close()

    return result


if __name__ == '__main__':
    print(main())

