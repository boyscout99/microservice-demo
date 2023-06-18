#!/bin/bash

PROTO_FILE="demo.proto"
SERVICE_ADDR="$PRODUCT_CATALOG_SERVICE_ADDR"
REQUEST_PAYLOAD='{"id":"0PUK6V6EV0"}'
SERVICE_METHOD="hipstershop.ProductCatalogService.GetProduct"

# Define the number of requests to send
REQUEST_COUNT=1000

for ((i=1; i<=REQUEST_COUNT; i++)); do
    grpcurl -v -plaintext -proto "$PROTO_FILE" -d "$REQUEST_PAYLOAD" "$SERVICE_ADDR" "$SERVICE_METHOD"
done