import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH, ORE_TYPES, DEFAULT_ORE_PROBABILITIES


class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH

        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"DB Dir Crated: {db_dir}")

        print(f"DB Pfad: {self.db_path}")

        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS servers
                       (
                           server_id
                           INTEGER
                           PRIMARY
                           KEY,
                           gamemaster_id
                           INTEGER
                           NOT
                           NULL,
                           setup_timestamp
                           TEXT
                           NOT
                           NULL
                       )
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           server_id
                           INTEGER
                           NOT
                           NULL,
                           username
                           TEXT
                           NOT
                           NULL,
                           join_timestamp
                           TEXT
                           NOT
                           NULL,
                           PRIMARY
                           KEY
                       (
                           user_id,
                           server_id
                       ),
                           FOREIGN KEY
                       (
                           server_id
                       ) REFERENCES servers
                       (
                           server_id
                       )
                           )
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS resources
                       (
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           server_id
                           INTEGER
                           NOT
                           NULL,
                           coal
                           INTEGER
                           DEFAULT
                           0,
                           iron
                           INTEGER
                           DEFAULT
                           0,
                           gold
                           INTEGER
                           DEFAULT
                           0,
                           copper
                           INTEGER
                           DEFAULT
                           0,
                           diamond
                           INTEGER
                           DEFAULT
                           0,
                           emerald
                           INTEGER
                           DEFAULT
                           0,
                           last_mine_timestamp
                           TEXT,
                           PRIMARY
                           KEY
                       (
                           user_id,
                           server_id
                       ),
                           FOREIGN KEY
                       (
                           server_id
                       ) REFERENCES servers
                       (
                           server_id
                       ),
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       )
                           )
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS ore_probabilities
                       (
                           server_id
                           INTEGER
                           PRIMARY
                           KEY,
                           coal
                           INTEGER
                           DEFAULT
                           40,
                           iron
                           INTEGER
                           DEFAULT
                           25,
                           gold
                           INTEGER
                           DEFAULT
                           15,
                           copper
                           INTEGER
                           DEFAULT
                           10,
                           diamond
                           INTEGER
                           DEFAULT
                           7,
                           emerald
                           INTEGER
                           DEFAULT
                           3,
                           FOREIGN
                           KEY
                       (
                           server_id
                       ) REFERENCES servers
                       (
                           server_id
                       )
                           )
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS gamemaster_tokens
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           gamemaster_id
                           INTEGER
                           NOT
                           NULL,
                           server_id
                           INTEGER
                           NOT
                           NULL,
                           token
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           created_at
                           TEXT
                           NOT
                           NULL,
                           FOREIGN
                           KEY
                       (
                           server_id
                       ) REFERENCES servers
                       (
                           server_id
                       )
                           )
                       """)

        conn.commit()
        conn.close()
        print("Datenbank initial")

    def server_exists(self, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM servers WHERE server_id = ?", (server_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def add_server(self, server_id, gamemaster_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO servers (server_id, gamemaster_id, setup_timestamp)
                           VALUES (?, ?, ?)
                           """, (server_id, gamemaster_id, datetime.now().isoformat()))

            cursor.execute("""
                           INSERT INTO ore_probabilities (server_id, coal, iron, gold, copper, diamond, emerald)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """, (server_id, *DEFAULT_ORE_PROBABILITIES.values()))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_all_servers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servers")
        servers = cursor.fetchall()
        conn.close()
        return [dict(s) for s in servers]

    def get_server_info(self, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servers WHERE server_id = ?", (server_id,))
        server = cursor.fetchone()
        conn.close()
        return dict(server) if server else None

    def get_server_gamemaster(self, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT gamemaster_id FROM servers WHERE server_id = ?", (server_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def user_in_game(self, user_id, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT 1
                       FROM users
                       WHERE user_id = ?
                         AND server_id = ?
                       """, (user_id, server_id))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def add_user_to_game(self, user_id, server_id, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO users (user_id, server_id, username, join_timestamp)
                           VALUES (?, ?, ?, ?)
                           """, (user_id, server_id, username, datetime.now().isoformat()))

            cursor.execute("""
                           INSERT INTO resources (user_id, server_id)
                           VALUES (?, ?)
                           """, (user_id, server_id))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_server_users(self, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT u.user_id,
                              u.username,
                              u.join_timestamp,
                              r.coal,
                              r.iron,
                              r.gold,
                              r.copper,
                              r.diamond,
                              r.emerald
                       FROM users u
                                LEFT JOIN resources r ON u.user_id = r.user_id AND u.server_id = r.server_id
                       WHERE u.server_id = ?
                       """, (server_id,))
        users = cursor.fetchall()
        conn.close()
        return [dict(u) for u in users]

    def get_user_resources(self, user_id, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT *
                       FROM resources
                       WHERE user_id = ?
                         AND server_id = ?
                       """, (user_id, server_id))
        resources = cursor.fetchone()
        conn.close()
        return dict(resources) if resources else None

    def add_ore(self, user_id, server_id, ore_type, amount):
        if ore_type not in ORE_TYPES:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE resources SET {ore_type} = {ore_type} + ?, last_mine_timestamp = ?
            WHERE user_id = ? AND server_id = ?
        """, (amount, datetime.now().isoformat(), user_id, server_id))
        conn.commit()
        conn.close()
        return True

    def set_ore(self, user_id, server_id, ore_type, amount):
        if ore_type not in ORE_TYPES:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE resources SET {ore_type} = ?
            WHERE user_id = ? AND server_id = ?
        """, (amount, user_id, server_id))
        conn.commit()
        conn.close()
        return True

    def get_ore_probabilities(self, server_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT *
                       FROM ore_probabilities
                       WHERE server_id = ?
                       """, (server_id,))
        probs = cursor.fetchone()
        conn.close()
        return dict(probs) if probs else None

    def update_ore_probability(self, server_id, ore_type, probability):
        if ore_type not in ORE_TYPES:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE ore_probabilities SET {ore_type} = ?
            WHERE server_id = ?
        """, (probability, server_id))
        conn.commit()
        conn.close()
        return True

    def create_gamemaster_token(self, gamemaster_id, server_id, token):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO gamemaster_tokens (gamemaster_id, server_id, token, created_at)
                           VALUES (?, ?, ?, ?)
                           """, (gamemaster_id, server_id, token, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def verify_token(self, token):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT gamemaster_id, server_id
                       FROM gamemaster_tokens
                       WHERE token = ?
                       """, (token,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_gamemaster_tokens(self, gamemaster_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT *
                       FROM gamemaster_tokens
                       WHERE gamemaster_id = ?
                       """, (gamemaster_id,))
        tokens = cursor.fetchall()
        conn.close()
        return [dict(t) for t in tokens]