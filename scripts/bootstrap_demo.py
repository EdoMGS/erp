#!/usr/bin/env python3
"""Bootstrap a demo environment with sample data.

This helper runs database migrations, loads a minimal fixture
and creates a default superuser. It is intended for onboarding
new developers so they can quickly have a working demo instance.

Environment variables:
    DATABASE_URL  - connection string for Postgres (libpq format)
    REDIS_URL     - Redis connection (default: redis://localhost:6379/0)
    DJANGO_SETTINGS_MODULE - Django settings module (default: erp_system.settings.base)
"""
from __future__ import annotations

import os
import subprocess
import sys


def run(cmd: list[str]) -> None:
    """Run a subprocess and stream output."""
    process = subprocess.run(cmd, check=True)


def main() -> int:
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "erp_system.settings.base")
    env.setdefault("REDIS_URL", "redis://localhost:6379/0")
    if "DATABASE_URL" not in env:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 1

    commands = [
        ["python", "manage.py", "migrate", "--noinput"],
    ]
    fixture = "erp_system/fixtures/minimal.json"
    if os.path.exists(fixture):
        commands.append(["python", "manage.py", "loaddata", fixture])
    commands.append(
        [
            "python",
            "manage.py",
            "createsuperuser",
            "--noinput",
            "--username",
            "admin",
            "--email",
            "admin@example.com",
        ]
    )

    for cmd in commands:
        print("$", " ".join(cmd))
        try:
            subprocess.run(cmd, env=env, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"Command {cmd} failed with {exc.returncode}", file=sys.stderr)
            return exc.returncode
    print("Demo bootstrap complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
