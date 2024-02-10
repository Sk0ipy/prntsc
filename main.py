# import all the necessary libraries
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
def generate_strings():
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [str(i) for i in range(10)]
    for a in characters:
        for b in characters:
            for c in characters:
                for d in characters:
                    for e in characters:
                        yield a + b + c + d + e


# create a function to generate the url
def generate_url():
    gen = generate_strings()
    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        while True:
            url = base_url + next(gen) + ".jpg"
            yield url


# create a function to check if the url is being redirected to "https://i.imgur.com/removed.png"
def check_url(url):
    response = requests.get(url)
    if response.url == "https://i.imgur.com/removed.png":
        return False
    else:
        return True


def main():
    try:
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
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS working_urls (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

            # create a table called SFW
            cursor.execute("CREATE TABLE IF NOT EXISTS sfw (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")
            # create a table called NSFW
            cursor.execute("CREATE TABLE IF NOT EXISTS nsfw (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

        urls = generate_url()

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:
            while True:
                url = next(urls)
                counter += 1
                urls_array.append(url)
                if len(urls_array) == 50:
                    url_tuple = [(url,) for url in urls_array]
                    cursor.executemany("INSERT INTO urls (url) VALUES (%s)", url_tuple)
                    connection.commit()
                    urls_array = []  # Clear the array after inserting its contents into the database

                if check_url(url):
                    # save the working url to the database
                    cursor.execute("INSERT INTO working_urls (url) VALUES (%s)", (url,))
                    connection.commit()
                    working_urls += 1

                # every 60 seconds print the number of urls checked and the number of working urls
                if time.time() - minute_timer > 15:
                    print(f"{counter} urls checked, {working_urls} working urls")
                    print(f"Running for {time.time() - start_time} seconds")
                    # average time per url
                    print(f"Average time per url: {(time.time() - start_time) / counter}")
                    minute_timer = time.time()
                    print("--------------------------------------------------")

    except KeyboardInterrupt:
        print("Program stopped")
        print(f"{counter} urls checked, {working_urls} working urls")
        print(f"Running for {time.time() - start_time} seconds")
        print(f"Average time per url: {(time.time() - start_time) / counter}")

    except Exception as e:
        # wait for 5 seconds before running the program where it left off
        print(e)
        time.sleep(5)
        # main()
        pass




if __name__ == '__main__':
    main()
