#!/bin/bash

set -e

# Run this from the root of this repo.
# i.e. ./docker/build_image.sh

# download AdventureWorks DW dababase backup and build a sql server docker image
# that has this backup restored to it.

echo "Downloading Adventureworks2019DW Data Warehouse backup..."
wget -O ./docker/AdventureWorksDW2019.bak -q https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorksDW2019.bak
docker build --no-cache ./docker/ -t pyreql-test-sqlserver -f ./docker/sqlserver.dockerfile
rm ./docker/AdventureWorksDW2019.bak

