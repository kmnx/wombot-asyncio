# tests/test_db_shazamids.py
import pytest
import asyncio
from helpers.db_shazamids import DB_ShazamIDs


@pytest.mark.asyncio
async def test_shazamids_full(tmp_path):
    db_path = tmp_path / "test_idhistory.db"
    db = DB_ShazamIDs(str(db_path))
    await db.open()
    await db.conn.execute(
        "CREATE TABLE IF NOT EXISTS chuntfm (id INTEGER PRIMARY KEY, timestamp_utc, username, request_source, request_command, station, show_name, artist, title, bandcamp, shazam_result, verified);"
    )
    test_data = [
        "2023-09-06T15:02:26Z",
        "anon1111",
        "chuntoo",
        "id1",
        "chuntfm",
        "anon livestream",
        "unknown artists",
        "good music",
        "http://bla",
        "shazam says bla",
        None,
    ]
    await db.insert_id_request(*test_data)
    # Test query_history_all
    all_results = await db.query_history_all()
    assert all_results is not None
    assert any(row[2] == "anon1111" for row in all_results)
    # Test query_usernames
    usernames = await db.query_usernames()
    assert usernames is not None
    assert ("anon1111",) in usernames or any("anon1111" in u for u in usernames)
    # Test query_history_user
    user_results = await db.query_history_user("anon1111")
    assert user_results is not None
    assert all(row[2] == "anon1111" for row in user_results)
    await db.close()
