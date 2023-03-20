#!/bin/sh

make docker-compose-up -C .. 
make docker-netcat-tests -C .. 
