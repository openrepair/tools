#!/bin/bash

SOLR_VERSION='9.2.1'
SOLR_DIR="solr-${SOLR_VERSION}"

if [[ ! -d "${SOLR_DIR}" ]]; then
	echo "${SOLR_DIR} not found"
else
	echo "Stopping Solr..."
	"${SOLR_DIR}/bin/solr" stop
	echo "Waiting for service stopped..."
	sleep 5 &
	wait
	rm -R "${SOLR_DIR}"
fi
