import mysql.connector
import mysql.connector.pooling
import requests

# create a connection to the database
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    host="localhost",
    user="root",
    database="prntsc_db"
)

base_url = "https://i.imgur.com/"  # base url for the images


def check_url(url):
    response = requests.get(url)
    print(response.url)
    if response.url == "https://i.imgur.com/removed.png":
        return False
    else:
        return True


def main():
    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        while True:
            try:
                cursor.execute("SELECT code from codes LIMIT 1")
                code = cursor.fetchone()
                if not code:
                    break
                code = code[0]
                url = base_url + code + ".jpg"
                print(url)
                if check_url(url):
                    cursor.execute("INSERT INTO working_urls (url) VALUES (%s)", (url,))
                    # remove the code from the database
                    cursor.execute("DELETE FROM codes WHERE code = %s", (code,))
                    connection.commit()
                    print(url)
                else:
                    # remove the code from the database
                    cursor.execute("DELETE FROM codes WHERE code = %s", (code,))
                    connection.commit()

            except Exception as e:
                print(e)





if __name__ == '__main__':
    main()
