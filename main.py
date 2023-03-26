# import all the necessary libraries
import random
import string

import mysql.connector
import requests

# create a database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="prntsc_db"
)

# create a table called urls
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS urls (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

# create a table called working_urls
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS working_urls (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255))")

base_url = "https://i.imgur.com/"  # base url for the images


# create a function to generate a random string of letters and numbers
def randomString(stringLength=7):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))


# this function will check if the url is already in the database and return True if it is
# if its true it will create a new url and check it again
def check_url_double(url):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT url FROM working_urls")
    myresult = mycursor.fetchall()
    for x in myresult:
        if url in x:
            return True
        else:
            return False


# create a function to generate the url
def generate_url():
    while True:
        url = base_url + randomString() + ".jpg"
        if not check_url_double(url):
            return url


# create a function to check if the url is being redirected to "https://i.imgur.com/removed.png"
def check_url(url):
    response = requests.get(url)
    if response.url == "https://i.imgur.com/removed.png":
        return False
    else:
        return True


def main():
    counter = 0  # initialize the counter variable
    working_urls = 0  # initialize the working_urls variable
    while True:
        url = generate_url()
        # checks if the url is already in the database if not add it to the database
        if not check_url_double(url):
            # add the url to the database
            mycursor = mydb.cursor()
            sql = "INSERT INTO urls (url) VALUES (%s)"
            val = (url,)
            mycursor.execute(sql, val)
            mydb.commit()

            if check_url(url):
                counter += 1  # increment the counter if the url is valid
                # insert the url into the database
                mycursor = mydb.cursor()
                sql = "INSERT INTO working_urls (url) VALUES (%s)"
                val = (url,)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")

                working_urls += 1  # increment the working_urls variable

                continue
            else:
                counter += 1  # increment the counter if the url is invalid

                # print counter to see how many urls have been checked
                print("Checked: " + url)
                print(working_urls, "working urls found")
                print(counter, "urls checked")
                continue
        else:
            print("Url already in database")
            continue


if __name__ == '__main__':
    main()
