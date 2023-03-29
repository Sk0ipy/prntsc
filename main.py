# import all the necessary libraries
import random
import string
import time

import mysql.connector
import mysql.connector.pooling
import requests

# create a connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="prntsc_db_pool",
    pool_size=5,
    host="localhost",
    user="root",
    database="prntsc_db"
)

base_url = "https://i.imgur.com/"  # base url for the images
string_length = 5  # the number must be 5 or higher for the program to work


# create a function to generate a random string of letters and numbers
def randomstring(stringLength=string_length):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for _ in range(stringLength)))


# this function will check if the url is already in the database and return True if it is
# if its true it will create a new url and check it again
def check_url_double(url, cursor):
    cursor.execute("SELECT url FROM working_urls WHERE url=%s", (url,))
    return cursor.fetchone() is not None


# create a function to generate the url
def generate_url():
    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        while True:
            url = base_url + randomstring() + ".jpg"
            if not check_url_double(url, cursor):
                return url


# create a function to check if the url is being redirected to "https://i.imgur.com/removed.png"
def check_url(url):
    response = requests.get(url)
    if response.url == "https://i.imgur.com/removed.png":
        return False
    else:
        return True


def main():
    # keep track of how long the program is running
    start_time = time.time()

    counter = 0  # initialize the counter variable
    working_urls = 0  # initialize the working_urls variable
    urls_array = []
    minute_timer = time.time()

    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        # create a table called urls
        cursor.execute("CREATE TABLE IF NOT EXISTS urls (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

        # create a table called working_urls
        cursor.execute("CREATE TABLE IF NOT EXISTS working_urls (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

    while True:

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:
            url = generate_url()
            # checks if the url is already in the database if not add it to the database
            if not check_url_double(url, cursor):
                # print the time it is running for in seconds
                counter += 1
                # save url to a array
                urls_array.append(url)
                if len(urls_array) == 50:
                    url_tuple = [(url,) for url in urls_array]
                    cursor.executemany("INSERT INTO urls (url) VALUES (%s)", url_tuple)
                    connection.commit()
                    urls_array = []

                if check_url(url):
                    # save the working url to the database
                    cursor.execute("INSERT INTO working_urls (url) VALUES (%s)", (url,))
                    connection.commit()
                    working_urls += 1

#                 every 60 seconds print the number of urls checked and the number of working urls
                if time.time() - minute_timer > 15:
                    print(f"{counter} urls checked, {working_urls} working urls")
                    print(f"Running for {time.time() - start_time} seconds")
#                   average time per url
                    print(f"Average time per url: {(time.time() - start_time) / counter}")
                    minute_timer = time.time()
                    print("--------------------------------------------------")


if __name__ == '__main__':
    main()
