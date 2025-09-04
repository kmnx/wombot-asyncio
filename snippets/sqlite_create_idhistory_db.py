import sqlite3
from sqlite3 import Error
from pathlib import Path
import os.path


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def run():
    conn_obj = create_connection("./data/database_idhistory.db")
    cursor_obj = conn_obj.cursor()
    cursor_obj.execute("DROP TABLE IF EXISTS chuntfm")
    cursor_obj.execute(
        "CREATE TABLE IF NOT EXISTS chuntfm (id INTEGER PRIMARY KEY, timestamp_utc, username, request_source, request_command, station, show_name, artist, title, bandcamp, shazam_result, verified);"
    )

    conn_obj.commit()
    cursor_obj.close()
    print("Database created successfully")


if __name__ == "__main__":
    run()
