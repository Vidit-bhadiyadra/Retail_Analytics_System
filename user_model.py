from utils.db import mysql


class UserModel:
    @staticmethod
    def get_user_by_credentials(username, password):
        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT id, username, full_name, role
            FROM users
            WHERE username = %s AND password = %s
            """,
            (username, password),
        )

        user = cur.fetchone()
        cur.close()

        return user