CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    author TEXT NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (username) REFERENCES users (username)
);