import asyncio
import os
import tarfile
from datetime import datetime

import aiosqlite

DB_FILE = "data/vault.db"
STORAGE_DIR = "data/vault_data"


async def main():
    # Pripoji se do databaze
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        db.row_factory = aiosqlite.Row
        # Vybere vsechny soubory starsi jak 30 dni
        async with db.execute(
            "SELECT * FROM files WHERE upload_date < datetime('now', '-30 days')"
        ) as cursor:
            old_files = await cursor.fetchall()
            if not old_files:
                print("No files to archive")
                return

            # vytvori .tar.gz archiv s jmenem <mesic>_<rok>.tar.gz
            month_year = datetime.now().strftime("%b_%Y")
            archive_filename = f"Archive_{month_year}.tar.gz"
            archive_path = os.path.join(STORAGE_DIR, archive_filename)

            print(f"Archiving {len(list(old_files))} files into {archive_filename}...")

            # otevre archiv
            with tarfile.open(archive_path, "w:gz") as tar:
                # prida kazdy soubor do archivu
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
