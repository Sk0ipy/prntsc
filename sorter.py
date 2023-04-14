# this will sort the pictures in the database by nsfw or sfw
# url [20:] skipt tot .com/
import os
import time
import urllib.request

import mysql.connector
import mysql.connector.pooling
from PIL import ImageFile
from nudenet import NudeClassifier

# create a connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="prntsc_db_pool",
    pool_size=5,
    host="localhost",
    user="root",
    database="prntsc_db"
)
c = NudeClassifier()

ImageFile.LOAD_TRUNCATED_IMAGES = True


def download_image(url):
    # download the image from the url and save it to the images folder
    urllib.request.urlretrieve(url, "images/" + url[20:])


def main():
    # if the images folder doesnt exist then create it
    if not os.path.exists("images"):
        os.makedirs("images")
    start_time = time.time()
    urls_array = []
    nsfw_counter = 0
    sfw_counter = 0
    total_counter = 0
    try:

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:
            # create a table called SFW
            cursor.execute("CREATE TABLE IF NOT EXISTS sfw (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")
            # create a table called NSFW
            cursor.execute("CREATE TABLE IF NOT EXISTS nsfw (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

        while True:
            with connection_pool.get_connection() as connection, connection.cursor() as cursor:
                # get the first url from the database
                cursor.execute("SELECT url FROM working_urls LIMIT 1")
                url = cursor.fetchone()
                if url is None:
                    break
                url = url[0]
                # delete the url from the database
                cursor.execute("DELETE FROM working_urls WHERE url=%s", (url,))
                # commit the changes
                connection.commit()
                # add the url to the urls_array
                urls_array.append(url)
                # download the image from the url
                download_image(url)
                # check if the image is nsfw or sfw
                result = c.classify("images/" + url[20:])
                print(result)

                unsafeValue = list(result.values())[0]['unsafe']  # get the unsafe value from the result

                # if the uservalue isnt unsafe then set it to 0
                if unsafeValue is None:
                    unsafeValue = 0

                # if the image is nsfw with a probability of 60% or higher (0.6)
                if unsafeValue > 0.6:
                    # add the url to the nsfw table
                    cursor.execute("INSERT INTO nsfw (url) VALUES (%s)", (url,))
                    # commit the changes
                    connection.commit()
                    # increase the nsfw_counter by 1
                    nsfw_counter += 1
                    total_counter += 1
                else:
                    # add the url to the sfw table
                    cursor.execute("INSERT INTO sfw (url) VALUES (%s)", (url,))
                    # commit the changes
                    connection.commit()
                    # increase the sfw_counter by 1
                    sfw_counter += 1
                    total_counter += 1
                # commit the changes
                connection.commit()
                # delete the image from the images folder to save space
                os.remove("images/" + url[20:])
                print(f"total: {total_counter} nsfw: {nsfw_counter} sfw: {sfw_counter}")

    except Exception as e:
        # print the error and continue the program
        print(e)
    finally:
        # print the time it took to run the program
        print(f"--- {time.time() - start_time} seconds ---")
        print(f"total: {total_counter} nsfw: {nsfw_counter} sfw: {sfw_counter}"
              f" {round((nsfw_counter / total_counter) * 100, 2)}% nsfw")
        try:
            # delete every image in the images folder
            for file in os.listdir("images"):
                os.remove("images/" + file)
        except Exception as e:
            exit()




if __name__ == "__main__":
    main()
