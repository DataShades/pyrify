import sqlite3


def create_test_db():
    # Create an in-memory SQLite database (change to "test.db" to save it)
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # 1. Create session table
    cursor.execute(
        """
        CREATE TABLE session (
            session_id TEXT PRIMARY KEY
        );
    """
    )

    # Insert some session data
    cursor.executemany(
        "INSERT INTO session (session_id) VALUES (?);",
        [
            ("abc123",),
            ("def456",),
        ],
    )

    # 2. Create user table
    cursor.execute(
        """
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            about TEXT
        );
    """
    )

    # Insert some users
    cursor.executemany(
        """
        INSERT INTO user (name, email, phone, address, about)
        VALUES (?, ?, ?, ?, ?);
    """,
        [
            (
                "Alice",
                "alice@example.com",
                "1234567890",
                "123 Main St",
                "Loves Python.",
            ),
            ("Bob", "bob@example.com", "9876543210", "456 Elm St", "Enjoys databases."),
        ],
    )

    # 3. Create a dummy revisions table
    cursor.execute(
        """
        CREATE TABLE revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        );
    """
    )

    # Commit and show success
    conn.commit()
    print("Tables created and populated.")
