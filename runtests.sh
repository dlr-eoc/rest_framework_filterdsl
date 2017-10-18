#!/bin/bash

pushd tests
pytest -s -vvv $*
