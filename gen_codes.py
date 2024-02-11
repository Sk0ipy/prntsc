import mysql.connector
import mysql.connector.pooling

# create a connection to the database
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    host="localhost",
    user="root",
    database="prntsc_db"
)


def gen_code(start_code=None):
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [str(i) for i in range(10)]
    start = [0, 0, 0, 0, 0, 0]
    if start_code:
        for i in range(6):
            if 'a' <= start_code[i] <= 'z':
                start[i] = ord(start_code[i]) - ord('a')
            else:
                start[i] = ord(start_code[i]) - ord('0') + 26

    for a in range(start[0], len(characters)):
        for b in range(start[1] if a == start[0] else 0, len(characters)):
            for c in range(start[2] if b == start[1] else 0, len(characters)):
                for d in range(start[3] if c == start[2] else 0, len(characters)):
                    for e in range(start[4] if d == start[3] else 0, len(characters)):
                        for f in range(start[5] if e == start[4] else 0, len(characters)):
                            yield characters[a] + characters[b] + characters[c] + characters[d] + characters[e] + characters[f]

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
    gen = gen_code("8st5h9")
    chunk_size = 30000  # Adjust the chunk size as per your needs
    with connection_pool.get_connection() as connection, connection.cursor() as cursor:
        for chunk in chunk_generator(gen, chunk_size):
            codes = [(code,) for code in chunk]
            cursor.executemany("INSERT INTO codes (code) VALUES (%s)", codes)
            connection.commit()


if __name__ == '__main__':
    main()
