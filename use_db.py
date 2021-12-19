import sqlite3


conn = sqlite3.connect('tasks.db')
cur = conn.cursor()
cur.execute("""
DROP TABLE IF EXISTS users;
""")

cur.execute("""
DROP TABLE IF EXISTS key_words;
""")

cur.execute("""
DROP TABLE IF EXISTS user_word;
""")

cur.execute("""
DROP TABLE IF EXISTS subscribes;
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
   userid TEXT NOT NULL UNIQUE,
   username TEXT,
   isactive BOOL);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS key_words(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   word TEXT NOT NULL UNIQUE);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_word(
    word_id INTEGER,
    chat_id INTEGER,
    PRIMARY KEY (word_id, chat_id)
    FOREIGN KEY(word_id) REFERENCES key_words(id),
    FOREIGN KEY(chat_id) REFERENCES users(id));   

""")


cur.execute("""
CREATE TABLE IF NOT EXISTS subscribes(
    word TEXT,
    chat_id INTEGER,
    isactive BOOL,
    PRIMARY KEY (word, chat_id));   

""")

conn.commit()