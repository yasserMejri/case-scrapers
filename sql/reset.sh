#!/bin/sh
echo "====================""
echo "dropping tables"
echo "====================""

HOST="eta-db-2.cluster-chtfyvkynsgx.us-west-2.rds.amazonaws.com"
echo $HOST
psql -U postgres -d postgres -h $HOST  -f drop.sql
echo "===================="
echo "adding states"
psql -U postgres -d postgres -h $HOST -f us_states.sql
echo "creating tables"
psql -U postgres -d postgres -h $HOST -f setup.sql
