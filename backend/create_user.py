import asyncio
import getpass

import aiosqlite
import bcrypt

DB_FILE = "data/vault.db"


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def main():
    username = input("Enter new username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match. Aborting.")
        return

    if not password:
        print("Password cannot be empty.")
        return

    hashed_pw = hash_password(password)

    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        try:
            await db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_pw),
            )
            await db.commit()
            print(f"Success! User '{username}' can now log in.")
        except aiosqlite.IntegrityError:
            print(f"Error: The user '{username}' already exists in the database.")


if __name__ == "__main__":
    asyncio.run(main())
