# Kubernetes anti-preempter

A bit of python that runs as a CronJob in Kubernetes that may or may not kill a node randomly - this is to avoid a situation where all the nodes in a GKE pre-emptible node pool die at the same time (after 24 hours), impacting service.

---

## Usage

A bash wrapper script `./go` is provided that provides some help:

- `./go init` to get local python virtual env up and running
- `./go run -t` runs it using locally specified credentials in dry-run mode. Remove the `-t` to allow it to actually delete nodes, if you have permission to do so
- `./go build` will build the docker image locally. This won't run locally as it relies on either being in-cluster or your .kube config for permissions
- `./go test` runs tests as a one-off, with `./go watch-tests` a useful way to have these running continually in the background

---

## To Do

- [ ] Deploy into Kubernetes as a CronJob
- [ ] CI from Github this time
- [ ] Full set of tests (coverage needs boosting)
- [ ] What happens if it kills the node its running on?
