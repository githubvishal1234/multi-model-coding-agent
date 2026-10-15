from app.config import load_log_level
from app.db import connect


def start():
    return f"[{load_log_level()}] {connect()}"


if __name__ == "__main__":
    print(start())
