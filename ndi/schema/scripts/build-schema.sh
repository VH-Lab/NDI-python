#!/bin/bash
# This file must be run from ndi-python/ndi/schema

for file in ./schema/*.fbs
  do
    flatc --python -o ./build $file
  done
