# This file is generated by SciPy's build process
# It contains system_info results at the time of building this package.
from enum import Enum

__all__ = ["show"]
_built_with_meson = True


class DisplayModes(Enum):
    stdout = "stdout"
    dicts = "dicts"


def _cleanup(d):
    """
    Removes empty values in a `dict` recursively
    This ensures we remove values that Meson could not provide to CONFIG
    """
    if isinstance(d, dict):
        return { k: _cleanup(v) for k, v in d.items() if v != '' and _cleanup(v) != '' }
    else:
        return d


CONFIG = _cleanup(
    {
        "Compilers": {
            "c": {
                "name": "clang",
                "linker": "ld64",
                "version": "14.0.0",
                "commands": "cc",
            },
            "cython": {
                "name": "cython",
                "linker": "cython",
                "version": "0.29.36",
                "commands": "cython",
            },
            "c++": {
                "name": "clang",
                "linker": "ld64",
                "version": "14.0.0",
                "commands": "c++",
            },
            "fortran": {
                "name": "gcc",
                "linker": "ld64",
                "version": "12.1.0",
                "commands": "gfortran",
            },
            "pythran": {
                "version": "0.14.0",
                "include directory": r"../../pip-build-env-xp5pbjk1/overlay/lib/python3.11/site-packages/pythran"
            },
        },
        "Machine Information": {
            "host": {
                "cpu": "aarch64",
                "family": "aarch64",
                "endian": "little",
                "system": "darwin",
            },
            "build": {
                "cpu": "aarch64",
                "family": "aarch64",
                "endian": "little",
                "system": "darwin",
            },
            "cross-compiled": bool("0".lower().replace('false', '')),
        },
        "Build Dependencies": {
            "blas": {
                "name": "openblas",
                "found": bool("1".lower().replace('false', '')),
                "version": "0.3.21.dev",
                "detection method": "pkgconfig",
                "include directory": r"/opt/arm64-builds/include",
                "lib directory": r"/opt/arm64-builds/lib",
                "openblas configuration": "USE_64BITINT= DYNAMIC_ARCH=1 DYNAMIC_OLDER= NO_CBLAS= NO_LAPACK= NO_LAPACKE= NO_AFFINITY=1 USE_OPENMP= SANDYBRIDGE MAX_THREADS=3",
                "pc file directory": r"/opt/arm64-builds/lib/pkgconfig",
            },
            "lapack": {
                "name": "openblas",
                "found": bool("1".lower().replace('false', '')),
                "version": "0.3.21.dev",
                "detection method": "pkgconfig",
                "include directory": r"/opt/arm64-builds/include",
                "lib directory": r"/opt/arm64-builds/lib",
                "openblas configuration": "USE_64BITINT= DYNAMIC_ARCH=1 DYNAMIC_OLDER= NO_CBLAS= NO_LAPACK= NO_LAPACKE= NO_AFFINITY=1 USE_OPENMP= SANDYBRIDGE MAX_THREADS=3",
                "pc file directory": r"/opt/arm64-builds/lib/pkgconfig",
            },
            "pybind11": {
                "name": "pybind11",
                "version": "2.11.0",
                "detection method": "config-tool",
                "include directory": r"unknown",
            },
        },
        "Python Information": {
            "path": r"/private/var/folders/76/zy5ktkns50v6gt5g8r0sf6sc0000gn/T/cibw-run-gft7gyfb/cp311-macosx_arm64/build/venv/bin/python",
            "version": "3.11",
        },
    }
)


def _check_pyyaml():
    import yaml

    return yaml


def show(mode=DisplayModes.stdout.value):
    """
    Show libraries and system information on which SciPy was built
    and is being used

    Parameters
    ----------
    mode : {`'stdout'`, `'dicts'`}, optional.
        Indicates how to display the config information.
        `'stdout'` prints to console, `'dicts'` returns a dictionary
        of the configuration.

    Returns
    -------
    out : {`dict`, `None`}
        If mode is `'dicts'`, a dict is returned, else None

    Notes
    -----
    1. The `'stdout'` mode will give more readable
       output if ``pyyaml`` is installed

    """
    if mode == DisplayModes.stdout.value:
        try:  # Non-standard library, check import
            yaml = _check_pyyaml()

            print(yaml.dump(CONFIG))
        except ModuleNotFoundError:
            import warnings
            import json

            warnings.warn("Install `pyyaml` for better output", stacklevel=1)
            print(json.dumps(CONFIG, indent=2))
    elif mode == DisplayModes.dicts.value:
        return CONFIG
    else:
        raise AttributeError(
            f"Invalid `mode`, use one of: {', '.join([e.value for e in DisplayModes])}"
        )
