# Changelog

## Unreleased

- Install crun 1.29.1 alongside runc with verified amd64/arm64 release-asset checksums.
- Add `containerd_default_runtime` (`runc` or `crun`) and separate OCI runtime handlers with systemd cgroups.
- Preserve runc as the default and retain its executable and handler when selecting crun.
- Add crun artifact verification and document runtime selection and staged migration.

## v2.3.5-rel.0

### Changes

- Update containerd to 2.3.5 and runc to 1.5.1 with amd64/arm64 checksum verification.
- Migrate the default configuration to containerd v4 and current CRI and gRPC server plugins.
- Use systemd cgroups, the current Kubernetes pause image, and configurable binary/socket paths.
- Require Ansible core 2.21 and Linux.
- Replace legacy CI tooling with pinned actions, uv-managed Python 3.14.7 and locked dependencies.
- Add pre-commit YAML/file checks, ansible-lint, actionlint, zizmor. Replace placeholder Molecule assertions with binary/configuration checks on Ubuntu 24.04.

### Upgrade notes

This is a breaking modernization of the previous release. Review custom variables
and templates before upgrading. Existing Kubernetes clusters must upgrade one
minor version at a time; this role is not a shortcut from the old 1.24 baseline.
Configuration and role tests do not certify a full Ubuntu/Flatcar HA cluster rollout.
