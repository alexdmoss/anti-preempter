# Kubernetes anti-preempter

A bit of python that runs as a CronJob in Kubernetes that may or may not kill a node randomly - this is to avoid a situation where all the nodes in a GKE pre-emptible node pool die at the same time (after 24 hours), impacting service.

---

## Usage

- `./go run -d=DIR` will scan DIR for duplicates
- `./go run -d=DIR -o=output.txt` will scan DIR for duplicates and output list of files found to output.txt
- if you don't want to mess about with Python/pipenv, then `./go build` will create a dockerised version that can be run in the same way as `./go run` but with `./go docker-run`
  - note that for saving of output with Docker using the `./go` wrapper, it expects -o to be a file in the `./output/` directory, e.g.
    `./go run-docker -d=test/ -o=./output/results.txt`

Run `./go init` to get started, and `./go watch-tests` to have continually running tests in the background.

---

## To Do

- [ ] Framework code
- [ ] Logic running locally as test-run
- [ ] Logic running in docker as test-run
- [ ] Introduce actual node kill
- [ ] What happens if it kills the node its running on?
- [ ] CI from Github this time
