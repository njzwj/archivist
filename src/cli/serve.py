import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Serve a local directory over HTTP.")
    parser.add_argument(
        "argv",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the Django management command.",
    )
    return parser.parse_args()


def serve():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.server.settings")
    args = parse_args()
    # print(f"Serving on port {args.port}")
    from django.core.management import execute_from_command_line

    execute_from_command_line(args.argv)
