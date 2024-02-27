import itertools
from multiprocessing.pool import ThreadPool
import time
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
    print("Generating codes...")  # Toegevoegd
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [str(i) for i in range(10)]
    counter = 0  # Toegevoegd
    for code in itertools.product(characters, repeat=5):  # Veranderd naar 6
        counter += 1  # Verhoog de teller
        if counter % 1000000 == 0:  # Print elke miljoen codes
            print(f"Generated {counter} codes so far...")
        yield ''.join(code)


def chunk_generator(iterable, chunk_size):
    print("Generating chunks...")  # Toegevoegd
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def worker(chunk):
    print(f"Starting worker function with {len(chunk)} codes...")
    # Create a new connection for each worker
    connection = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",
        database="codes"
    )

    with connection.cursor() as cursor:
        # Create a list of tuples for the batch operation
        codes = [(code,) for code in chunk]
        print(f"Inserting {len(codes)} codes into the database...")  # Toegevoegd

        # Use executemany to perform the batch operation
        cursor.executemany("INSERT INTO code5 (code) VALUES (%s)", codes)  # Veranderd naar code6

        # Commit the transaction
        connection.commit()

    # Close the connection when done
    connection.close()


def main():
    print("Starting main function...")
    start_time = time.time()  # Starttijd opslaan

    gen = gen_code()
    chunk_size = 30000  # Verkleind naar 1000

    # Maak een ThreadPool
    pool = ThreadPool()

    # Gebruik de map-functie van de pool om het werk toe te wijzen aan de worker-functie
    print("Starting ThreadPool map...")  # Toegevoegd
    pool.map(worker, chunk_generator(gen, chunk_size))
    print("Finished ThreadPool map...")  # Toegevoegd

    # Sluit de pool en wacht tot alle workers klaar zijn
    pool.close()
    pool.join()

    end_time = time.time()  # Eindtijd opslaan

    elapsed_time = end_time - start_time  # Bereken de verstreken tijd
    print(f"Het programma duurde {elapsed_time // 3600} uur en {(elapsed_time % 3600) // 60} minuten.")

def test_database_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="1234",
            database="codes"
        )
        connection.close()
        print("Database is bereikbaar.")
    except Exception as e:
        print("Kan geen verbinding maken met de database. Controleer de databasegegevens en de netwerkverbinding.")
        print("Foutdetails:", e)



test_database_connection()

if __name__ == '__main__':
    main()