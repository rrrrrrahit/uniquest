from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    """
    Makes `python manage.py runserver` accessible from other devices
    in the local network by default.
    """

    default_addr = "0.0.0.0"

    def run_from_argv(self, argv):
        # If no address/port is provided, bind to all interfaces.
        if len(argv) == 2:
            argv = [*argv, "0.0.0.0:8000"]
        super().run_from_argv(argv)
