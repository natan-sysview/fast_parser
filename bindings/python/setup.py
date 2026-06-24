from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent


def native_library_name() -> str:
    if platform.system() == "Windows":
        return "fastparse.dll"
    if platform.system() == "Darwin":
        return "libfastparse.dylib"
    return "libfastparse.so"


def default_platform_tag() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin":
        if machine in {"arm64", "aarch64"}:
            return "macosx_11_0_arm64"
        return "macosx_10_15_x86_64"
    if system == "Windows":
        return "win_amd64" if machine in {"amd64", "x86_64"} else f"win_{machine}"
    if machine in {"x86_64", "amd64"}:
        return "manylinux2014_x86_64"
    if machine in {"aarch64", "arm64"}:
        return "manylinux2014_aarch64"
    return f"linux_{machine}"


def python_package_version() -> str:
    version = os.environ.get("FASTPARSE_PY_VERSION", "0.1.0-preview.13")
    if "-preview." in version:
        base, preview = version.split("-preview.", 1)
        return f"{base}rc{preview}"
    if "-preview" in version:
        base, preview = version.split("-preview", 1)
        return f"{base}rc{preview.lstrip('.') or '0'}"
    return version


class build_py(_build_py):
    def run(self) -> None:
        build_command = self.get_finalized_command("build")
        build_temp = Path(build_command.build_temp).resolve()
        build_temp.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["cmake", "-S", str(ROOT), "-B", str(build_temp), "-DCMAKE_BUILD_TYPE=Release"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            ["cmake", "--build", str(build_temp), "--config", "Release", "--target", "tsmp"],
            cwd=ROOT,
            check=True,
        )

        super().run()

        version_target = Path(self.build_lib) / "fastparse" / "_version.py"
        version_target.parent.mkdir(parents=True, exist_ok=True)
        version_target.write_text(f'__version__ = "{python_package_version()}"\n', encoding="utf-8")

        native_name = native_library_name()
        source = ROOT / "bin" / native_name
        if not source.is_file():
            raise FileNotFoundError(f"native FastParse library was not built: {source}")

        target_dir = Path(self.build_lib) / "fastparse" / "native"
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_dir / native_name)


class bdist_wheel(_bdist_wheel):
    def finalize_options(self) -> None:
        super().finalize_options()
        self.root_is_pure = False
        if not self.plat_name:
            self.plat_name = os.environ.get("FASTPARSE_PY_PLATFORM_TAG") or default_platform_tag()

    def get_tag(self) -> tuple[str, str, str]:
        _python_tag, _abi_tag, platform_tag = super().get_tag()
        return "py3", "none", os.environ.get("FASTPARSE_PY_PLATFORM_TAG") or platform_tag


setup(
    version=python_package_version(),
    package_data={"fastparse": ["native/*"]},
    include_package_data=True,
    cmdclass={"build_py": build_py, "bdist_wheel": bdist_wheel},
)
