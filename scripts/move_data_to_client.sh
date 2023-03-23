#!/bin/bash

# https://stackoverflow.com/questions/24112727/relative-paths-based-on-file-location-instead-of-current-working-directory
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd "../.data"
unzip "dataset.zip"
mkdir -p ../client/.data
cp * ../client/.data


