#!/bin/bash
# health-test.sh
# Version: v1.2.9
# Purpose: Verify that rag-api container is running and API endpoints respond

API="http://localhost:5005"

echo "== RAG API Health Test (v1.2.9) =="

echo -n "[1/3] Checking /health ... "
curl -s -o /dev/null -w "%{http_code}\n" "$API/health"

echo -n "[2/3] Checking /ingest (dry-run) ... "
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$API/ingest" \
    -H "Content-Type: application/json" \
    -d '{}'

echo -n "[3/3] Checking /query ... "
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$API/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}'

echo "Done."



##############  You can mark the file as executable:
##############     cd /opt/rag-api
##############    chmod +x health-test.sh
##############  You can then execute it like this:
##############    ./health-test.sh