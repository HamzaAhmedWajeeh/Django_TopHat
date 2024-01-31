import time
from typing import Any

from django.db import OperationalError as mssqlOperationalError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from pyodbc import OperationalError as PyODBERROR


class Command(BaseCommand):
    """
    Django Command to wait for database

    Args:
        BaseCommand (_type_): _description_
    """
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Waiting for db...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(OperationalError, mssqlOperationalError, PyODBERROR):
                self.stdout.write(
                    "Database unavailable waiting for 1 second...."
                    )
                time.sleep(3)

        self.stdout.write(self.style.SUCCESS('Database Available!!!'))
