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

echo "Installing ORDS core..."

cp -R ./core/ords "${SOLR_DIR}/server/solr"

ls -l "${SOLR_DIR}/server/sol"

echo "Starting Solr..."

ls -l "${SOLR_DIR}/bin"

# Arg 'solr.jetty.host' allows WSL browser interface.
"${SOLR_DIR}/bin/solr" start -Dsolr.jetty.host="0.0.0.0"

echo "Waiting for service loaded..."

sleep 10 &

wait

"${SOLR_DIR}/bin/solr" status

echo "Importing ORDS data..."

# If this fails due to still waiting for service, copy and paste to command line.
curl 'http://localhost:8983/solr/ords202303/update?commit=true' --data-binary @../dat/ords/OpenRepairData_v0.3_aggregate_202303.csv -H 'Content-type:application/csv'

# Retrieve system status
# curl 'http://localhost:8983/solr/admin/info/system'

# Retrieve core status
# curl 'http://localhost:8983/solr/ords202303/admin/system'