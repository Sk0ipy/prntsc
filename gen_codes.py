import psycopg2
from psycopg2 import pool

  

# create a connection to the database
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    host="localhost",
    user="postgres",
    password="1234",
    database="codes"
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
    chunk_size = 30000  # Adjust the chunk size as per your needs
    with connection_pool.getconn() as connection:
        with connection.cursor() as cursor:
            for chunk in chunk_generator(gen, chunk_size):
                codes = [(code,) for code in chunk]
                cursor.executemany("INSERT INTO code5 (code) VALUES (%s)", codes)
                connection.commit()
        connection_pool.putconn(connection)


if __name__ == '__main__':
    main()
