import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Serve a local directory over HTTP.")
    parser.add_argument(
        "argv",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the Django runserver command.",
    )
    return parser.parse_args()


def serve():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.server.settings")
    args = parse_args()
    argv = ["manage.py", "runserver"] + args.argv

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)
