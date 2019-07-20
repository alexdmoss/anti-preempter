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
  echo -e "    deploy               Deploys app to Kubernetes. Designed to run in Drone CI"
  echo -e "    watch-tests          Watch pytest run for faster feedback"
  echo -e "    push                 Push latest built docker image to Container Registry"
  echo -e "    init                 Set up local virtual env"
  echo -e 
  exit 0
}

function init() {

  _console_msg "Initialising local virtual environment ..." INFO true

  pushd "$(dirname $BASH_SOURCE[0])" > /dev/null
  pipenv install --dev
  popd > /dev/null

  _console_msg "Init complete" INFO true

}

function run() {

  _console_msg "Running python:main ..." INFO true

  pushd "$(dirname $BASH_SOURCE[0])" > /dev/null

  pipenv run python3 main.py "$@"

  popd > /dev/null
  
  _console_msg "Execution complete" INFO true

}

function watch-tests() {

  pushd "$(dirname $BASH_SOURCE[0])" > /dev/null
  
  _console_msg "Following unit tests ..." INFO true

  pipenv run ptw

  popd > /dev/null

}

# NB: Dockerfile also runs these, so do not need to use in CI
function test() {

  pushd "$(dirname $BASH_SOURCE[0])" > /dev/null

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

function push() {

    _assert_variables_set GCP_PROJECT_NAME

    pushd $(dirname $BASH_SOURCE[0]) >/dev/null

    _console_msg "Pushing image to registry ..."

    if [[ ${CI_SERVER:-} == "yes" ]]; then
        echo "${GOOGLE_CREDENTIALS}" | gcloud auth activate-service-account --key-file -
        trap "gcloud auth revoke --verbosity=error" EXIT
    fi

    gcloud auth configure-docker --quiet

    docker tag ${IMAGE_NAME}:latest eu.gcr.io/${GCP_PROJECT_NAME}/${IMAGE_NAME}:latest

    docker push eu.gcr.io/${GCP_PROJECT_NAME}/${IMAGE_NAME}:latest

    popd >/dev/null 

}

function deploy() {

  _assert_variables_set GCP_PROJECT_ID GOOGLE_CREDS NAMESPACE

  pushd $(dirname $BASH_SOURCE[0]) >/dev/null

  # when running in CI, we need to set up gcloud/kubeconfig
  if [[ ${DRONE:-} == "true" ]]; then

    _assert_variables_set K8S_DEPLOYER_CREDS K8S_CLUSTER_NAME

    _console_msg "-> Authenticating with GCloud"
    echo "${K8S_DEPLOYER_CREDS}" | gcloud auth activate-service-account --key-file -

    region=$(gcloud container clusters list --project=${GCP_PROJECT_ID} --filter "NAME=${K8S_CLUSTER_NAME}" --format "value(zone)")

    _console_msg "-> Authenticating to cluster ${K8S_CLUSTER_NAME} in project ${GCP_PROJECT_ID} in ${region}"
    gcloud container clusters get-credentials ${K8S_CLUSTER_NAME} --project=${GCP_PROJECT_ID} --region=${region}

  fi

  _console_msg "Applying Kubernetes yaml"
  cat k8s/*.yaml | envsubst | kubectl apply -n ${NAMESPACE} -f -

  _console_msg "Setting up secrets"

  kubectl delete secret -n=${NAMESPACE} anti-preempter-creds || true
  kubectl create secret -n=${NAMESPACE} generic anti-preempter-creds \
                        --from-literal=google_creds="${GOOGLE_CREDS}"

  popd >/dev/null

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

if [[ ${1:-} =~ ^(help|run|build|test|watch-tests|push|init|deploy)$ ]]; then
  COMMAND=${1}
  shift
  $COMMAND "$@"
else
  help
  exit 1
fi
