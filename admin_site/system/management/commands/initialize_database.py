# Copyright (C) 2024 Magenta ApS, https://magenta.dk.
# Contact: info@magenta.dk.

import os
import glob

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from os2borgerpc_admin.settings import install_dir

fixtures_dirs = [
    os.path.join(install_dir, "system/fixtures"),
    os.path.join(install_dir, "changelog/fixtures"),
]


class Command(BaseCommand):
    """
        Initialize database.
        Helper command to seed database with (static) basic data.

        :Reference: :mod:`os2borgerpc_admin.initialize`

        Should be able to be run multiple times over without generating
    duplicates.

        Example:

                    $ python manage.py initialize_database

    """

    help = """Populate the database with initial data."""

    def handle(self, *args, **options):
        """Initialize all the basic data we want at start.

        Should be able to be run multiple times over without
        generating duplicates.
        """
        if not settings.INITIALIZE_DATABASE:
            return

        # Create a file in the container when the database is initialized so it only happens once, when a given container is created. We want it in the container as opposed to the host so its rerun when the container is recreated.
        # Otherwise it attempts to read in fixtures every time the container starts, which can cause issues (e.g. integrity errors) if you've made changes to the db
        try:
            open("/tmp/initialized", "r")
        except FileNotFoundError:
            open("/tmp/initialized", "w").close()

            print("Populate database with (static) basic data:")

            for dir in fixtures_dirs:
                if os.path.exists(dir) and os.path.isdir(dir):
                    for file in sorted(glob.glob(os.path.join(dir, "*.json"))):
                        if os.path.isfile(file):
                            call_command("loaddata", file)

            # Inform user that the operation is complete
            # Assuming that if any of the underlying functions fail
            # the process is stopped/caught in place
            print("Database populated with (static) basic data")
