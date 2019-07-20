# Kubernetes anti-preempter

A bit of python that runs as a CronJob in Kubernetes that may or may not kill a node randomly - this is to avoid a situation where all the nodes in a GKE pre-emptible node pool die at the same time (after 24 hours), impacting service.

---

## Usage

A bash wrapper script `./go` is provided that provides some help:

- `./go init` to get local python virtual env up and running
- `./go run -t` runs it using locally specified credentials in dry-run mode. Remove the `-t` to allow it to actually delete nodes, if you have permission to do so
- `./go build` will build the docker image locally. The image will not run locally as it relies on either being in-cluster or your .kube config for permissions, but this is useful for testing the Dockerfile
- `./go test` runs tests as a one-off, with `./go watch-tests` a useful way to have these running continually in the background. The Dockerfile has a stage to run `pytest` so the build will fail if they fail or coverage is too low

---

## To Do

- [ ] Image Tag in deploy
- [ ] Drone: define secrets through API
- [ ] Drone: deal with gated builds
- [ ] DockerHub: Add Dockerfile
- [ ] Full set of tests (coverage needs boosting)

## Useful Stuff

This is quite handy to validate out-of-band:

```sh
gcloud compute instances list --project="${GCP_PROJECT_ID}" --filter="PREEMPTIBLE:true" --format='value(creationTimestamp.date(format=%s),name,zone,status)'| sort
```

