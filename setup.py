#!/usr/bin/env python
import datetime
import json
import os
import os.path
import shutil
import sys
import traceback
from distutils import log
from distutils.command.build import build as BuildCommand
from distutils.core import Command
from subprocess import check_output

from setuptools import find_packages, setup
from setuptools.command.develop import develop as DevelopCommand
from setuptools.command.sdist import sdist as SDistCommand

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


# modified from:
# https://raw.githubusercontent.com/getsentry/sentry/055cfe74bb88bbb2083f37f5df21b91d0ef4f9a7/src/sentry/utils/distutils/commands/base.py
class BaseBuildCommand(Command):
    user_options = [
        ("work-path=", "w", "The working directory for source files. Defaults to ."),
        ("build-lib=", "b", "directory for script runtime modules"),
        (
            "inplace",
            "i",
            "ignore build-lib and put compiled javascript files into the source "
            + "directory alongside your pure Python modules",
        ),
        (
            "force",
            "f",
            "Force rebuilding of static content. Defaults to rebuilding on version "
            "change detection.",
        ),
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
        return []

    def get_manifest_additions(self):
        return []

    def finalize_options(self):
        # This requires some explanation.  Basically what we want to do
        # here is to control if we want to build in-place or into the
        # build-lib folder.  Traditionally this is set by the `inplace`
        # command line flag for build_ext.  However as we are a subcommand
        # we need to grab this information from elsewhere.
        #
        # An in-place build puts the files generated into the source
        # folder, a regular build puts the files into the build-lib
        # folder.
        #
        # The following situations we need to cover:
        #
        #   command                         default in-place
        #   setup.py build_js               0
        #   setup.py build_ext              value of in-place for build_ext
        #   setup.py build_ext --inplace    1
        #   pip install --editable .        1
        #   setup.py install                0
        #   setup.py sdist                  0
        #   setup.py bdist_wheel            0
        #
        # The way this is achieved is that build_js is invoked by two
        # subcommands: bdist_ext (which is in our case always executed
        # due to a custom distribution) or sdist.
        #
        # Note: at one point install was an in-place build but it's not
        # quite sure why.  In case a version of install breaks again:
        # installations via pip from git URLs definitely require the
        # in-place flag to be disabled.  So we might need to detect
        # that separately.
        #
        # To find the default value of the inplace flag we inspect the
        # sdist and build_ext commands.
        sdist = self.distribution.get_command_obj("sdist")
        build_ext = self.get_finalized_command("build_ext")

        # If we are not decided on in-place we are inplace if either
        # build_ext is inplace or we are invoked through the install
        # command (easiest check is to see if it's finalized).
        if self.inplace is None:
            self.inplace = (build_ext.inplace or sdist.finalized) and 1 or 0

        # If we're coming from sdist, clear the hell out of the dist
        # folder first.
        if sdist.finalized:
            for path in self.get_dist_paths():
                try:
                    shutil.rmtree(path)
                except (OSError, IOError):
                    pass

        # In place means build_lib is src.  We also log this.
        if self.inplace:
            log.debug("in-place js building enabled")
            self.build_lib = "src"
        # Otherwise we fetch build_lib from the build command.
        else:
            self.set_undefined_options("build", ("build_lib", "build_lib"))
            log.debug("regular js build: build path is %s" % self.build_lib)

        if self.work_path is None:
            self.work_path = self.get_root_path()

    def _needs_built(self):
        for path in self.get_dist_paths():
            if not os.path.isdir(path):
                return True
        return False

    def _setup_git(self):
        work_path = self.work_path

        if os.path.exists(os.path.join(work_path, ".git")):
            log.info("initializing git submodules")
            self._run_command(["git", "submodule", "init"])
            self._run_command(["git", "submodule", "update"])

    def _setup_js_deps(self):
        node_version = None
        try:
            node_version = self._run_command(["node", "--version"]).decode("utf-8").rstrip()
        except OSError:
            log.fatal("Cannot find node executable. Please install node" " and try again.")
            sys.exit(1)

        if node_version[2] is not None:
            log.info("using node ({0})".format(node_version))
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
        # if we were invoked from sdist, we need to inform sdist about
        # which files we just generated.  Otherwise they will be missing
        # in the manifest.  This adds the files for what webpack generates
        # plus our own assets.json file.
        sdist = self.distribution.get_command_obj("sdist")
        if not sdist.finalized:
            return

        # The path down from here only works for sdist:

        # Use the underlying file list so that we skip the file-exists
        # check which we do not want here.
        files = sdist.filelist.files
        base = os.path.abspath(".")

        # We need to split off the local parts of the files relative to
        # the current folder.  This will chop off the right path for the
        # manifest.
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
        (
            "asset-json-path=",
            None,
            "Relative path for JSON manifest. Defaults to {dist_name}/assets.json",
        ),
        (
            "inplace",
            "i",
            "ignore build-lib and put compiled javascript files into the source "
            + "directory alongside your pure Python modules",
        ),
        (
            "force",
            "f",
            "Force rebuilding of static content. Defaults to rebuilding on version "
            "change detection.",
        ),
    ]

    description = "build static media assets"

    def initialize_options(self):
        self.work_path = os.path.join(ROOT_PATH, "src/dispatch/static/dispatch")
        self.asset_json_path = os.path.join(self.work_path, "assets.json")
        BaseBuildCommand.initialize_options(self)

    def get_dist_paths(self):
        return [os.path.join(self.work_path, "/dist")]

    def get_manifest_additions(self):
        return (self.asset_json_path,)

    def _get_package_version(self):
        """
        Attempt to get the most correct current version of Dispatch.
        """
        pkg_path = os.path.join(ROOT_PATH, "src")

        sys.path.insert(0, pkg_path)
        try:
            import dispatch
        except Exception:
            version = None
            build = None
        else:
            log.info(f"pulled version information from 'dispatch' module. {dispatch.__file__}")
            version = self.distribution.get_version()
            build = dispatch.__build__
        finally:
            sys.path.pop(0)

        if not (version and build):
            json_path = self.get_asset_json_path()
            try:
                with open(json_path) as fp:
                    data = json.loads(fp.read())
            except Exception:
                pass
            else:
                log.info("pulled version information from '{}'".format(json_path))
                version, build = data["version"], data["build"]

        return {"version": version, "build": build}

    def _needs_static(self, version_info):
        json_path = self.get_asset_json_path()
        if not os.path.exists(json_path):
            return True

        with open(json_path) as fp:
            data = json.load(fp)
        if data.get("version") != version_info.get("version"):
            return True
        if data.get("build") != version_info.get("build"):
            return True
        return False

    def _needs_built(self):
        if BaseBuildCommand._needs_built(self):
            return True
        version_info = self._get_package_version()
        return self._needs_static(version_info)

    def _build(self):
        version_info = self._get_package_version()
        log.info(
            "building assets for {} v{} (build {})".format(
                self.distribution.get_name(),
                version_info["version"] or "UNKNOWN",
                version_info["build"] or "UNKNOWN",
            )
        )
        if not version_info["version"] or not version_info["build"]:
            log.fatal("Could not determine dispatch version or build")
            sys.exit(1)

        try:
            self._build_static()
        except Exception:
            traceback.print_exc()
            log.fatal("unable to build Dispatch's static assets!")
            sys.exit(1)

        log.info("writing version manifest")
        manifest = self._write_version_file(version_info)
        log.info("recorded manifest\n{}".format(json.dumps(manifest, indent=2)))

    def _build_static(self):
        # By setting NODE_ENV=production, a few things happen
        #   * Vue optimizes out certain code paths
        #   * Webpack will add version strings to built/referenced assets
        env = dict(os.environ)
        env["DISPATCH_STATIC_DIST_PATH"] = self.dispatch_static_dist_path
        env["NODE_ENV"] = "production"
        # TODO: Our JS builds should not require 4GB heap space
        env["NODE_OPTIONS"] = (
            (env.get("NODE_OPTIONS", "") + " --max-old-space-size=4096")
        ).lstrip()
        # self._run_npm_command(["webpack", "--bail"], env=env)

    def _write_version_file(self, version_info):
        manifest = {
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
            "version": version_info["version"],
            "build": version_info["build"],
        }
        with open(self.get_asset_json_path(), "w") as fp:
            json.dump(manifest, fp)
        return manifest

    @property
    def dispatch_static_dist_path(self):
        return os.path.abspath(os.path.join(self.build_lib, "src/static/dispatch/dist"))

    def get_asset_json_path(self):
        return os.path.abspath(os.path.join(self.build_lib, self.asset_json_path))


VERSION = "0.1.0.dev0"
IS_LIGHT_BUILD = os.environ.get("DISPATCH_LIGHT_BUILD") == "1"


def get_requirements(env):
    with open("requirements-{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements("base")
dev_requires = get_requirements("dev")


class DispatchSDistCommand(SDistCommand):
    # If we are not a light build we want to also execute build_assets as
    # part of our source build pipeline.
    if not IS_LIGHT_BUILD:
        sub_commands = SDistCommand.sub_commands + [("build_assets", None)]


class DispatchBuildCommand(BuildCommand):
    def run(self):
        if not IS_LIGHT_BUILD:
            self.run_command("build_assets")
        BuildCommand.run(self)


class DispatchDevelopCommand(DevelopCommand):
    def run(self):
        DevelopCommand.run(self)
        if not IS_LIGHT_BUILD:
            self.run_command("build_assets")


cmdclass = {
    "sdist": DispatchSDistCommand,
    "develop": DispatchDevelopCommand,
    "build": DispatchBuildCommand,
    "build_assets": BuildAssetsCommand,
}

# Get the long description from the README file
with open(os.path.join(ROOT_PATH, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dispatch",
    version=VERSION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Netflix, Inc.",
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    cmdclass=cmdclass,
    zip_safe=False,
    include_package_data=True,
    entry_points={
        "console_scripts": ["dispatch = dispatch.cli:entrypoint"],
        "dispatch.plugins": [
            "dispatch_document_resolver = dispatch.plugins.dispatch_core.plugin:DispatchDocumentResolverPlugin",
            "dispatch_participant_resolver = dispatch.plugins.dispatch_core.plugin:DispatchParticipantResolverPlugin",
            "dispatch_pkce_auth = dispatch.plugins.dispatch_core.plugin:PKCEAuthProviderPlugin",
            "dispatch_ticket = dispatch.plugins.dispatch_core.plugin:DispatchTicketPlugin",
            "dispatch_basic_auth = dispatch.plugins.dispatch_core.plugin:BasicAuthProviderPlugin",
            "dispatch_contact = dispatch.plugins.dispatch_core.plugin:DispatchContactPlugin",
            "google_calendar_conference = dispatch.plugins.dispatch_google.calendar.plugin:GoogleCalendarConferencePlugin",
            "google_docs_document = dispatch.plugins.dispatch_google.docs.plugin:GoogleDocsDocumentPlugin",
            "google_drive_storage = dispatch.plugins.dispatch_google.drive.plugin:GoogleDriveStoragePlugin",
            "google_drive_task = dispatch.plugins.dispatch_google.drive.plugin:GoogleDriveTaskPlugin",
            "google_gmail_email = dispatch.plugins.dispatch_google.gmail.plugin:GoogleGmailEmailPlugin",
            "google_groups_participants = dispatch.plugins.dispatch_google.groups.plugin:GoogleGroupParticipantGroupPlugin",
            "jira_ticket = dispatch.plugins.dispatch_jira.plugin:JiraTicketPlugin",
            "pagerduty_oncall = dispatch.plugins.dispatch_pagerduty.plugin:PagerDutyOncallPlugin",
            "slack_contact = dispatch.plugins.dispatch_slack.plugin:SlackContactPlugin",
            "slack_conversation = dispatch.plugins.dispatch_slack.plugin:SlackConversationPlugin",
            "zoom_conference = dispatch.plugins.dispatch_zoom.plugin:ZoomConferencePlugin",
            "opsgenie_oncall = dispatch.plugins.dispatch_opsgenie.plugin:OpsGenieOncallPlugin",
        ],
    },
)
