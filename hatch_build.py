import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildSharedObjectd(BuildHookInterface):
    def initialize(self, version, build_data):
        build_data["pure_python"] = False
        build_data["tag"] = "py3-none-linux_x86_64"

        subprocess.check_output(["make", "format-lib"])
