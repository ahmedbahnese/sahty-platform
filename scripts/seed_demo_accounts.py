#!/usr/bin/env python3
"""Create/update Sehaty trial role accounts from an environment secret.

Never put a password in this file or in source control. Set
SEHATY_BOOTSTRAP_PASSWORD in the target environment, run migrations first, and
then execute this script once. Existing account passwords are not overwritten.
"""

import os
import sys


PASSWORD_ENV = "SEHATY_BOOTSTRAP_PASSWORD"


def main():
    password = os.environ.get(PASSWORD_ENV)
    if not password:
        print(f"Missing required environment variable: {PASSWORD_ENV}", file=sys.stderr)
        return 2
    from main import app, initialize_application_data

    with app.app_context():
        initialize_application_data()
    print("Trial role accounts are ready. Passwords are read from the environment and were not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
