#!/usr/bin/env python

import os
import shutil
import sys
import json
from subprocess import check_output
from setuptools import find_packages, setup, Command
from setuptools.command.build import build as BuildCommand
from setuptools.command.develop import develop as DevelopCommand
from setuptools.command.sdist import sdist as SDistCommand

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

class BaseBuildCommand(Command):
    user_options = [
        ("work-path=", "w", "The working directory for source files. Defaults to ."),
        ("build-lib=", "b", "directory for script runtime modules"),
        ("inplace", "i", "ignore build-lib and put compiled javascript files into the source directory alongside your pure Python modules"),
        ("force", "f", "Force rebuilding of static content. Defaults to rebuilding on version change detection."),
    ]

    boolean_options = ["force"]

    def initialize_options(self):
        self.build_lib = None
        self.force = None
        self.work_path = os.path.join(ROOT_PATH, "src/dispatch/static/dispatch")
        self.inplace = None

    def get_root_path(self):
        return os.path.abspath(os.path.dirname(sys.modules["__main__"].__file__))

    def get_dist_paths(self):
        return [os.path.join(self.work_path, "dist")]

    def get_manifest_additions(self):
        return [os.path.join(self.work_path, "assets.json")]

    def finalize_options(self):
        sdist = self.distribution.get_command_obj("sdist")
        build_ext = self.get_finalized_command("build_ext")

        if self.inplace is None:
            self.inplace = (build_ext.inplace or sdist.finalized) and 1 or 0

        if sdist.finalized:
            for path in self.get_dist_paths():
                try:
                    shutil.rmtree(path)
                except (OSError, IOError):
                    pass

        if self.inplace:
            self.build_lib = "src"
        else:
            self.set_undefined_options("build", ("build_lib", "build_lib"))

        if self.work_path is None:
            self.work_path = self.get_root_path()

    def _needs_built(self):
        for path in self.get_dist_paths():
            if not os.path.isdir(path):
                return True
            if self._check_for_changes(path):
                return True
        return False

    def _check_for_changes(self, path):
        # Implement logic to check for changes in specific files or directories
        # Example: compare timestamps, checksums, or other criteria
        # This is a placeholder implementation
        return False

    def _setup_git(self):
        work_path = self.work_path

        if os.path.exists(os.path.join(work_path, ".git")):
            self._run_command(["git", "submodule", "init"])
            self._run_command(["git", "submodule", "update"])

    def _setup_js_deps(self):
        try:
            node_version = self._run_command(["node", "--version"]).decode("utf-8").rstrip()
            log.info(f"using node ({node_version})")
        except OSError:
            log.fatal("Cannot find node executable. Please install node and try again.")
            sys.exit(1)

        self._run_npm_command(["install"])
        self._run_npm_command(["run", "build", "--quiet"])

    def _run_command(self, cmd, env=None):
        cmd_str = " ".join(cmd)
        log.debug(f"running [{cmd_str}]")
        try:
            return check_output(cmd, cwd=self.work_path, env=env)
        except Exception:
            log.error(f"command failed [{cmd_str}] via [{self.work_path}]")
            raise

    def _run_npm_command(self, cmd, env=None):
        self._run_command(["npm"] + cmd, env=env)

    def update_manifests(self):
        sdist = self.distribution.get_command_obj("sdist")
        if not sdist.finalized:
            return

        files = sdist.filelist.files
        base = os.path.abspath(".")

        for path in self.get_dist_paths():
            for dirname, _, filenames in os.walk(os.path.abspath(path)):
                for filename in filenames:
                    filename = os.path.join(dirname, filename)
                    files.append(filename[len(base) :].lstrip(os.path.sep))

        for file in self.get_manifest_additions():
            files.append(file)

    def run(self):
        if self.force or self._needs_built():
            self._setup_git()
            self._setup_js_deps()
            self._build()
            self.update_manifests()

class BuildAssetsCommand(BaseBuildCommand):
    user_options = BaseBuildCommand.user_options + [
        ("asset-json-path=", None, "Relative path for JSON manifest. Defaults to {dist_name}/assets.json"),
        ("inplace", "i", "ignore build-lib and put compiled javascript files into the source directory alongside your pure Python modules"),
        ("force", "f", "Force rebuilding of static content. Defaults to rebuilding on version change detection."),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.asset_json_path = None

    def finalize_options(self):
        super().finalize_options()
        if self.asset_json_path is None:
            self.asset_json_path = os.path.join(self.build_lib, "assets.json")

    def run(self):
        super().run()
        self._generate_asset_manifest()

    def _generate_asset_manifest(self):
        manifest = {"assets": []}
        for path in self.get_dist_paths():
            for dirname, _, filenames in os.walk(os.path.abspath(path)):
                for filename in filenames:
                    manifest["assets"].append(os.path.relpath(os.path.join(dirname, filename), self.build_lib))

        with open(self.asset_json_path, "w") as f:
            json.dump(manifest, f)

class DispatchSDistCommand(SDistCommand):
    def run(self):
        self.run_command("build_assets")
        super().run()

class DispatchBuildCommand(BuildCommand):
    sub_commands = BuildCommand.sub_commands + [("build_assets", None)]

setup(
    name="your_package_name",
    version="0.1.0",
    packages=find_packages(),
    cmdclass={
        'build': DispatchBuildCommand,
        'develop': DevelopCommand,
        'sdist': DispatchSDistCommand,
        'build_assets': BuildAssetsCommand,
    },
)
