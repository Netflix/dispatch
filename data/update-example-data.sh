#!/usr/bin/env bash
echo "Dropping existing database..."
dispatch database drop
echo "Restoring current dump file..."
dispatch database restore --dump-file ./dispatch-sample-data.dump
echo "Running database migrations..."
dispatch database upgrade
echo "Dumping sql to file..."
dispatch database dump --dump-file ./dispatch-sample-data.dump
