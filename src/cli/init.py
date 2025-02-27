import os

ARCHIVIST_ENV_PATH = os.path.expanduser(
    os.getenv("ARCHIVIST_ENV_PATH", "~/.archivist.env")
)


def run_init():
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env.example")
    )
    dst_path = ARCHIVIST_ENV_PATH
    if os.path.exists(dst_path):
        print(f"{dst_path} already exists, skipping copy.")
        return
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(src_path, "r") as src_file:
        with open(dst_path, "w") as dst_file:
            dst_file.write(src_file.read())
    print(f"Copied .env.example to {dst_path}")


if __name__ == "__main__":
    run_init()
