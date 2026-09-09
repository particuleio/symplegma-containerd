"""Keep OCI runtime selection explicit without replacing existing runc handlers."""

import tomllib
import unittest
from pathlib import Path

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

ROOT = Path(__file__).resolve().parents[1]


def variables(arch="x86_64", **overrides):
    loader = DataLoader()
    data = loader.load_from_file(str(ROOT / "defaults/main.yaml"), trusted_as_template=True)
    data.update({"ansible_facts": {"architecture": arch}, "bin_dir": "/usr/local/bin"})
    data.update(overrides)
    return loader, data


def render(**overrides):
    loader, data = variables(**overrides)
    return Templar(loader=loader, variables=data).template(data["containerd_config"])


class ContainerdRuntimeTests(unittest.TestCase):
    def test_both_runtime_choices_preserve_distinct_handlers(self):
        for arch in ("x86_64", "aarch64"):
            for selected in ("runc", "crun"):
                with self.subTest(arch=arch, selected=selected):
                    config = tomllib.loads(
                        render(
                            arch=arch,
                            containerd_default_runtime=selected,
                            bin_dir="/custom/bin",
                        )
                    )
                    runtime = config["plugins"]["io.containerd.cri.v1.runtime"]["containerd"]
                    self.assertEqual(runtime["default_runtime_name"], selected)
                    for name in ("runc", "crun"):
                        handler = runtime["runtimes"][name]
                        self.assertEqual(handler["runtime_type"], "io.containerd.runc.v2")
                        self.assertEqual(handler["options"]["BinaryName"], f"/custom/bin/{name}")
                        self.assertIs(handler["options"]["SystemdCgroup"], True)

    def test_default_remains_runc(self):
        _, data = variables()
        self.assertEqual(data["containerd_default_runtime"], "runc")

    def test_invalid_selection_fails_before_host_changes(self):
        loader, data = variables()
        tasks = loader.load_from_file(
            str(ROOT / "tasks/main.yaml"), trusted_as_template=True
        )
        condition = tasks[0]["ansible.builtin.assert"]["that"][0]
        for selected in ("runc", "crun", "typo", ""):
            templar = Templar(
                loader=loader, variables={**data, "containerd_default_runtime": selected}
            )
            self.assertEqual(templar.evaluate_conditional(condition), selected in ("runc", "crun"))

    def test_crun_downloads_match_verified_release_assets(self):
        digests = {
            "amd64": "0a5ea25cafe618bbfbf1c747871155063619f18025ccdd8ad648c97633f35d57",
            "arm64": "1ea99c6fc7a8e17a4a1d666df09cccb0769a4db0aa738cf38c967a777a731b1d",
        }
        for arch, download_arch in (("x86_64", "amd64"), ("aarch64", "arm64")):
            loader, data = variables(arch=arch)
            tasks = loader.load_from_file(
                str(ROOT / "tasks/main.yaml"), trusted_as_template=True
            )
            task = next(task for task in tasks if task["name"] == "Containerd | Download crun")
            download = Templar(loader=loader, variables=data).template(
                task["ansible.builtin.get_url"]
            )
            self.assertEqual(
                download["url"],
                "https://github.com/containers/crun/releases/download/1.29.1/"
                f"crun-1.29.1-linux-{download_arch}",
            )
            self.assertEqual(download["checksum"], f"sha256:{digests[download_arch]}")
            self.assertEqual(download["dest"], "/usr/local/bin/crun")
            self.assertEqual(download["mode"], "0755")
            self.assertEqual(task["notify"], "restart containerd")


if __name__ == "__main__":
    unittest.main()
