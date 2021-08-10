import logging
from typing import List

from hubgrep import db
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TableHelper:
    """
    helper class for raw db requests

    use like
    ```
    with TableHelper._cursor() as cur:
        TableHelper.drop_table(cur, "some_table")
    ```

    commit runs on leaving context
    """
    @classmethod
    @contextmanager
    def _cursor(cls):
        con = db.engine.raw_connection()
        try:
            cur = con.cursor()
            yield cur
            con.commit()
        finally:
            con.close()

    @classmethod
    def drop_table(cls, cur, table_name):
        """
        drop table (if exists)
        """
        cur.execute(f"drop table if exists {table_name}")

    @classmethod
    def rename_table(cls, cur, old_table_name, new_table_name):
        """
        rename a table
        """
        cur.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name}")

    @classmethod
    def create_empty_temporary_repositories_table(cls, cur, table_name):
        """
        create an empty copy of the "repositories" table
        """

        # including defaults: https://stackoverflow.com/a/12265248
        cur.execute(
            f"""
                create temporary table {table_name}
                (like repositories including all)
                """
        )

    @classmethod
    def create_empty_repositories_table(cls, cur, table_name):
        """
        create an empty copy of the "repositories" table
        """

        # including defaults: https://stackoverflow.com/a/12265248
        cur.execute(
            f"""
            create unlogged table {table_name}
            (like repositories including all)
            """
        )

    @classmethod
    def rotate_tables(cls, cur, table_to_replace, table_with_new_data):
        """
        replace <table_to_replace> with <table_with_new_data>
        rename <table_with_new_data> to <table_to_replace>

        """
        logger.info(f"dropping {table_to_replace}")
        cls.drop_table(cur, table_to_replace)
        logger.info(f"renaming {table_with_new_data} to {table_to_replace}")
        cls.rename_table(cur, table_with_new_data, table_to_replace)
