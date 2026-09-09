# symplegma-containerd

[![CI](https://github.com/particuleio/symplegma-containerd/actions/workflows/ansible.yml/badge.svg)](https://github.com/particuleio/symplegma-containerd/actions/workflows/ansible.yml)

Linux role for [Symplegma](https://github.com/particuleio/symplegma).
Requires Ansible core 2.21 or newer. See [CHANGELOG.md](CHANGELOG.md) for versions,
breaking changes and upgrade constraints.

## OCI runtimes

The role installs checksum-verified runc and crun binaries for amd64/arm64 and
registers separate `runc` and `crun` handlers. runc remains the default, matching
containerd upstream. To explicitly select crun for the generated configuration:

```yaml
containerd_default_runtime: crun
```

Both handlers use `io.containerd.runc.v2`: this names containerd's shim, while
`BinaryName` selects the actual OCI executable. Both retain systemd cgroups.
The runc handler continues to point to runc; selecting crun never replaces the
runc executable. Custom `containerd_config` overrides must configure their own
handlers and `default_runtime_name`.

Changing the default restarts containerd through the normal handler, but does
not recreate existing pods. Validate crun using a `RuntimeClass` and a disposable
pod first, then plan workload recreation separately. Keep both executables and
handlers during the transition. Do not combine this change with a Kubernetes
minor upgrade.

crun's upstream benchmarks report lower startup time and runtime memory use;
these are not measurements of application throughput or this cluster. Keep runc
as the default until crun has been validated with your CNI, storage and workloads.
See [containerd's runtime configuration](https://github.com/containerd/containerd/blob/v2.3.5/docs/cri/config.md)
and [crun's benchmarks](https://github.com/containers/crun#performance).

## Development

Install [mise](https://mise.jdx.dev/), then run:

```sh
mise install
just setup
just lint
```

uv installs Python 3.14.7 and the locked dependencies. Without mise/just, use
`uv sync --locked` and `uv run --locked pre-commit run --all-files`.

Run `just unit` for offline OCI runtime selection and checksum tests. These also
run in pre-commit. Run `just test` for Molecule convergence and verification in a pinned Ubuntu
24.04 Docker image. This uses privileged containers and writable cgroups:
only run it on disposable development/CI hosts. These tests check installed
artifacts; they do not perform a full cluster upgrade or certify Flatcar.

## Releases

Prepare a reviewed, signed pull request with a changelog entry. Publish its
release tag only after required checks and review pass and the change is merged.
Symplegma's requirements must point to an existing published tag.
