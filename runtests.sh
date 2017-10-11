#!/bin/bash

pushd tests
pytest -vvv $*
