import asyncio
import sys
import time

import aiohttp
import asyncpg
import select

# Database connection parameters
connection_params = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '1234',
    'database': 'codes',
}

# Base URL for the images
base_url = "https://i.imgur.com/"
# Table with the codes
code_table = "code5"
# Number of concurrent HTTP requests
concurrent_requests = 10
# Batch size for processing codes
batch_size = 1000


async def fetch_and_process_codes(pool, session, codes, stats):
    async with pool.acquire() as connection:
        async with connection.transaction():
            for code in codes:
                if stats['checked'] >= stats['total']:
                    return
                await process_code(session, connection, code['code'], stats)


async def process_code(session, connection, code, stats):
    url = base_url + code + ".png"
    async with session.head(url, allow_redirects=True) as response:
        final_url = str(response.url)
        stats['checked'] += 1
        if final_url == "https://i.imgur.com/removed.png":
            connection.execute(f"DELETE FROM {code_table} WHERE code = $1", code)
            print(f"Code {code} URL is not valid.")
        else:
            await insert_url(connection, url)
            stats['valid'] += 1
            connection.execute(f"DELETE FROM {code_table} WHERE code = $1", code)
            print(f"Code {code} URL inserted.")


async def insert_url(connection, url):
    async with connection.transaction():
        await connection.execute("INSERT INTO working_urls (url) VALUES ($1)", url)


async def main():
    stats = {'total': 0, 'checked': 0, 'valid': 0}
    start_time = time.time()
    async with asyncpg.create_pool(**connection_params, min_size=1, max_size=20) as pool:
        async with aiohttp.ClientSession() as session:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    codes = await connection.fetch(f"SELECT code FROM {code_table}")
                    stats['total'] = len(codes)
                    print(f"Total codes to process: {stats['total']}")

                    # Process codes in batches
                    for i in range(0, stats['total'], batch_size):
                        batch = codes[i:i + batch_size]
                        await fetch_and_process_codes(pool, session, batch, stats)
                        if stats['checked'] >= stats['total']:
                            break
                        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                            if sys.stdin.readline().strip() == 'q':
                                break

    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken: {duration} seconds")
    print(f"Total codes checked: {stats['checked']}")
    print(f"Total valid codes: {stats['valid']}")
    print(f"Percentage of valid codes: {stats['valid'] / stats['checked'] * 100:.2f}%")


if __name__ == '__main__':
    asyncio.run(main())
