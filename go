#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -z ${IMAGE_NAME:-} ]]; then
  IMAGE_NAME=anti-preempter
fi 

SRC_DIR=anti-preempter

function help() {
  echo -e "Usage: go <command>"
  echo -e
  echo -e "    help                 Print this help"
  echo -e "    run                  Run locally from source"
  echo -e "    build                Build Docker image (won't push anywhere)"
  echo -e "    test                 Run local unit tests and linting"
  echo -e "    watch-tests          Watch pytest run for faster feedback"
  echo -e "    init                 Set up local virtual env"
  echo -e 
  exit 0
}

function init() {

  _console_msg "Initialising local virtual environment ..." INFO true

  pushd "${SRC_DIR}/" > /dev/null
  pipenv install --dev
  popd > /dev/null

  _console_msg "Init complete" INFO true

}

function run() {

  _console_msg "Running python:main ..." INFO true

  pushd "${SRC_DIR}/" > /dev/null

  pipenv run python3 main.py "$@"

  popd > /dev/null
  
  _console_msg "Execution complete" INFO true

}

function watch-tests() {

  pushd "${SRC_DIR}/" > /dev/null
  
  _console_msg "Following unit tests ..." INFO true

  pipenv run ptw

  popd > /dev/null

}

# NB: Dockerfile also runs these, so do not need to use in CI
function test() {

  pushd "${SRC_DIR}/" > /dev/null

  if [[ ${CI_JOB_TOKEN:-} != "" ]]; then
    pip install pipenv==2018.10.13
  fi

  pipenv install --dev

  _console_msg "Running flake8 ..." INFO true

  pipenv run flake8 .

  # _console_msg "Running type hinting validation ..." INFO true
  # pipenv run pytype --keep-going .

  _console_msg "Running unit tests ..." INFO true
  
  pipenv run pytest -s -v
  
  _console_msg "Tests complete" INFO true

  popd > /dev/null

}

function build() {

  pushd $(dirname $BASH_SOURCE[0]) > /dev/null

  _console_msg "Building docker image ..." INFO true

  docker build --tag ${IMAGE_NAME}:latest .

  _console_msg "Build complete" INFO true

  popd > /dev/null

}

function _assert_variables_set() {

  local error=0
  local varname
  
  for varname in "$@"; do
    if [[ -z "${!varname-}" ]]; then
      echo "${varname} must be set" >&2
      error=1
    fi
  done
  
  if [[ ${error} = 1 ]]; then
    exit 1
  fi

}

function _console_msg() {

  local msg=${1}
  local level=${2:-}
  local ts=${3:-}

  if [[ -z ${level} ]]; then level=INFO; fi
  if [[ -n ${ts} ]]; then ts=" [$(date +"%Y-%m-%d %H:%M")]"; fi

  echo ""

  if [[ ${level} == "ERROR" ]] || [[ ${level} == "CRIT" ]] || [[ ${level} == "FATAL" ]]; then
    (echo 2>&1)
    (echo >&2 "-> [${level}]${ts} ${msg}")
  else 
    (echo "-> [${level}]${ts} ${msg}")
  fi

  echo ""

}

function ctrl_c() {
    if [ ! -z ${PID:-} ]; then
        kill ${PID}
    fi
    exit 1
}

trap ctrl_c INT

if [[ ${1:-} =~ ^(help|run|build|test|watch-tests|init)$ ]]; then
  COMMAND=${1}
  shift
  $COMMAND "$@"
else
  help
  exit 1
fi
