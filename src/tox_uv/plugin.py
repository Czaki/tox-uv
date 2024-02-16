"""
Tox plugin to use uv instead of pip.

Implemented by overloading the pip installer to use uv instead of pip.
"""
from __future__ import annotations

import os.path
from typing import Any, Sequence

from tox.config.main import Config
from tox.config.types import Command
from tox.execute.request import StdinSource
from tox.plugin import impl
from tox.tox_env.python.api import Python
from tox.tox_env.python.pip.pip_install import Pip
from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner
from tox.tox_env.register import ToxEnvRegister


class UVInstaller(Pip):
    """Oberload of the pip installer to use uv instead of pip."""

    def __init__(self, tox_env: Python, with_list_deps: bool = True) -> None:
        """
        Initialize the uv installer.

        Parameters
        ----------
        tox_env : Python
            The python environment to use.
        with_list_deps : bool, optional
            If true, list the dependencies, by default True

        """
        self._with_list_deps = with_list_deps
        super().__init__(tox_env)

    def _register_config(self) -> None:
        self._env.conf.add_config(
            keys=["pip_pre"],
            of_type=bool,
            default=False,
            desc="install the latest available pre-release"
            " (alpha/beta/rc) of dependencies without a specified version",
        )
        self._env.conf.add_config(
            keys=["install_command"],
            of_type=Command,
            default=self.default_install_command,
            post_process=self.post_process_install_command,
            desc="command used to install packages",
        )
        self._env.conf.add_config(
            keys=["constrain_package_deps"],
            of_type=bool,
            default=False,
            desc="If true, apply constraints during install_package_deps.",
        )
        self._env.conf.add_config(
            keys=["use_frozen_constraints"],
            of_type=bool,
            default=False,
            desc="Use the exact versions of installed deps"
            " as constraints, otherwise use the listed deps.",
        )
        if self._with_list_deps:  # pragma: no branch
            self._env.conf.add_config(
                keys=["list_dependencies_command"],
                of_type=Command,
                default=Command(["python", "-m", "uv", "pip", "freeze"]),
                desc="command used to list installed packages",
            )

    def default_install_command(self, conf: Config, env_name: str | None) -> Command:
        """Get the default install command."""
        cmd = Command(
            ["python", "-I", "-m", "uv", "pip", "install", "{opts}", "{packages}"]
        )
        return self.post_process_install_command(cmd)

    def install(self, arguments: Any, section: str, of_type: str) -> None:
        """Install the package."""
        return super().install(arguments, section, of_type)

    def _execute_installer(self, deps: Sequence[Any], of_type: str) -> None:
        """
        Execute the installer.

        This is hack as uv doe not support installing from path.
        """
        print("Executing with uv", deps, of_type)
        if of_type == "package":
            deps = [_path_to_spcyfications(dep) for dep in deps]
        return super()._execute_installer(deps, of_type)


def _path_to_spcyfications(path: str) -> str:
    if not os.path.exists(path):
        return path
    if os.path.isfile(path):
        file_name = os.path.basename(path)
        name = file_name.split("-", maxsplit=1)[0]
        return f"{name} @ {path}"
    return path


class UVVirtualEnvRunner(VirtualEnvRunner):
    """A python virtual environment runner that uses the uv package instead of pip."""

    _installer: UVInstaller | None

    @staticmethod
    def id() -> str:
        """Get the id of the virtual environment runner."""
        return "uv-virtualenv"

    def _install(self, arguments: Any, section: str, of_type: str) -> None:
        return super()._install(arguments, section, of_type)

    @property
    def installer(self) -> UVInstaller:
        """Get the uv installer."""
        if self._installer is None:
            self._installer = UVInstaller(self)
        return self._installer

    def _setup_uv(self) -> None:
        cmd = Command(["python", "-m", "pip", "install", "uv"])
        self.execute(cmd.args, stdin=StdinSource.OFF, run_id="install_uv")

    def create_python_env(self) -> None:
        """Create the python environment."""
        res = super().create_python_env()
        self._paths = self.prepend_env_var_path()
        self._setup_uv()
        return res


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    """Register the uv virtual environment runner."""
    register.add_run_env(UVVirtualEnvRunner)
