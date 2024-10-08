CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    admin INTEGER NOT NULL,
    user_description TEXT,
    profile_picture TEXT
);

CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    song_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    entry INTEGER NOT NULL,
    private INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (title) REFERENCES songs(title),
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (author) REFERENCES songs(author)
);