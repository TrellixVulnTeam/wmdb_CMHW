#!/bin/bash
# Create clean database with basic generated data.

rm -f ym.db
cat ./create_schema.sql | sqlite3 ym.db
cat ./populate_tables.sql | sqlite3 ym.db
