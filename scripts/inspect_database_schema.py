import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app, db
from sqlalchemy import inspect


def main():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print('tables=', len(tables))
        for table in sorted(tables):
            indexes = inspector.get_indexes(table)
            foreign_keys = inspector.get_foreign_keys(table)
            unique_constraints = inspector.get_unique_constraints(table)
            check_constraints = inspector.get_check_constraints(table)
            print(f'{table}: columns={len(inspector.get_columns(table))} indexes={len(indexes)} foreign_keys={len(foreign_keys)} unique={len(unique_constraints)} checks={len(check_constraints)}')


if __name__ == '__main__':
    main()
