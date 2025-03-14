import os


def serve(argv):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.server.settings")
    argv = ["manage.py", "runserver"] + list(argv)

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)
