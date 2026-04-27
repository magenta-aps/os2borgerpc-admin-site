# Copyright (C) 2024 Magenta ApS, https://magenta.dk.
# Contact: info@magenta.dk.

import os
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Initialize database.
    Helper command to seed database with (static) basic data.

    :Reference: :mod:`os2borgerpc_admin.initialize`

    Example: $ ./manage.py initialize_database
    """

    help = """Populate the database with initial data."""

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            help="The path to a directory that will be recursively scanned for fixtures",
        )

    def handle(self, *args, **options):
        """Initialize all the basic data we want at start."""

        # Create a file in the container when the database is initialized so it only happens once, when a given container is created. We want it in the container as opposed to the host so its rerun when the container is recreated.
        # Otherwise it attempts to read in fixtures every time the container starts, which can cause issues (e.g. integrity errors) if you've made changes to the db
        try:
            open("/tmp/initialized", "r")
        except FileNotFoundError:
            fixtures_base_dir = Path(options["path"])
            print(
                f"Populate database with (static) basic data. Dir: {fixtures_base_dir}"
            )
            fixtures = sorted(fixtures_base_dir.rglob("*.json"))
            print(f"Found {len(fixtures)} fixtures files under the directory.")

            for file in fixtures:
                if os.path.isfile(file):
                    call_command("loaddata", file, verbosity=3)

            # Inform user that the operation is complete
            # Assuming that if any of the underlying functions fail
            # the process is stopped/caught in place
            print("Database populated with (static) basic data")

            open("/tmp/initialized", "w").close()
