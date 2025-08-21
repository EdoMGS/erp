from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase


class MigrationHealthTest(TestCase):
    def test_no_unapplied_migrations(self):
        """Ensure the test database reflects all migrations (graph fully applied)."""
        connection = connections["default"]
        executor = MigrationExecutor(connection)
        # Leaf nodes represent latest targets; migration_plan returns tuples of (node, backwards)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        unapplied = [migration for migration, backwards in plan if not backwards]
        self.assertEqual(
            unapplied, [], f"Unapplied migrations detected (apply or adjust): {unapplied}"
        )
