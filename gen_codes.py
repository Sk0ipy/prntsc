import mysql.connector
import mysql.connector.pooling

# create a connection to the database
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    host="localhost",
    user="root",
    database="prntsc_db"
)


def gen_code():
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [str(i) for i in range(10)]
    for a in characters:
        for b in characters:
            for c in characters:
                for d in characters:
                    for e in characters:
                        yield a + b + c + d + e


def chunk_generator(iterable, chunk_size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def main():
    gen = gen_code()
    chunk_size = 3000  # Adjust the chunk size as per your needs
    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        for chunk in chunk_generator(gen, chunk_size):
            codes = [(code,) for code in chunk]
            cursor.executemany("INSERT INTO codes (code) VALUES (%s)", codes)
            connection.commit()


if __name__ == '__main__':
    main()
