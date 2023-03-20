#!/bin/bash

TESTS=10
CORRECT=0

for i in `seq 1 $TESTS`
do
  N_CHARS=$(head /dev/urandom | tr -cd 1-9 | head -c2)
  TEST_STR="head /dev/urandom | tr -cd A-Za-z0-9 | head -c ${N_CHARS}"
  PAYLOAD=$(eval ${TEST_STR})
  RES=$(echo $PAYLOAD | nc server 12345)
  EXPECTED_RESPONSE="${PAYLOAD}"
  echo "Test ${i}"
  echo "Payload: $PAYLOAD"
  echo "Expected response: $EXPECTED_RESPONSE"
  echo "Response: $RES"
  if [ "$EXPECTED_RESPONSE" == "$RES" ]; then
    CORRECT=$(( CORRECT + 1 ))
  fi
done
echo "Test results: ${CORRECT}/${TESTS}"
