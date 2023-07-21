#!/bin/bash

# Java 17 or better preferred
java --version

# Look up most recent version at http://archive.apache.org/dist/lucene/solr/
SOLR_VERSION='9.2.1'
SOLR_DIR="solr-${SOLR_VERSION}"
SOLR_FILE="${SOLR_DIR}.tgz"

if [[ ! -f "${SOLR_FILE}" ]]; then
	echo "${SOLR_FILE} not found, downloading..."
	wget -O "${SOLR_FILE}" "https://www.apache.org/dyn/closer.lua/solr/solr/${SOLR_VERSION}/${SOLR_FILE}?action=download"
else
	echo "$SOLR_FILE found, extracting..."
fi

tar -xzf "${SOLR_FILE}" -C ./

ls -l "${SOLR_DIR}"

echo "Installing cores..."

cp -R ./core/test "${SOLR_DIR}/server/solr"
cp -R ./core/ords "${SOLR_DIR}/server/solr"

ls -l "${SOLR_DIR}/server/solr"

echo "Starting Solr..."

# Arg 'solr.jetty.host' allows WSL browser interface.
"${SOLR_DIR}/bin/solr" start -Dsolr.jetty.host="0.0.0.0"

echo "Waiting for service loaded..."

sleep 10 &

wait

"${SOLR_DIR}/bin/solr" status

# If imports fail due to still waiting for service, copy and paste to command line.

echo "Importing test data..."

curl 'http://localhost:8983/solr/test_lang/update?commit=true' --data-binary @./core/data/test_lang.csv -H 'Content-type:application/csv'

echo "Importing ORDS data..."

curl 'http://localhost:8983/solr/ords202303/update?commit=true' --data-binary @../dat/ords/OpenRepairData_v0.3_aggregate_202303.csv -H 'Content-type:application/csv'

# Retrieve system status
# curl 'http://localhost:8983/solr/admin/info/system'

# Retrieve core status
# curl 'http://localhost:8983/solr/ords202303/admin/system'