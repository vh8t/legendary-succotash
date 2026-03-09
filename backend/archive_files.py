import asyncio
import os
import tarfile
from datetime import datetime

import aiosqlite

DB_FILE = "data/vault.db"
STORAGE_DIR = "data/vault_data"


async def main():
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM files WHERE upload_date < datetime('now', '-30 days')"
        ) as cursor:
            old_files = await cursor.fetchall()
            if not old_files:
                print("No files to archive")
                return

            month_year = datetime.now().strftime("%b_%Y")
            archive_filename = f"Archive_{month_year}.tar.gz"
            archive_path = os.path.join(STORAGE_DIR, archive_filename)

            print(f"Archiving {len(list(old_files))} files into {archive_filename}...")

            with tarfile.open(archive_path, "w:gz") as tar:
                for file in old_files:
                    path = os.path.join(STORAGE_DIR, file["filename"])
                    if os.path.exists(path):
                        tar.add(path, arcname=file["filename"])
                        print(f"Added {file['filename']} to archive.")
                    else:
                        print(f"Warning: {file['filename']} missing from disk!")

            print(f"Successfully created {archive_filename}!")


if __name__ == "__main__":
    asyncio.run(main())
