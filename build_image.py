#!/usr/bin/env python3
"""Run octabam's build_bus.py with its image written to a private path.

    build_image.py OUT.bin        (cwd: the checkout; REMIX, XBUS, SPEC from the environment)

build_bus.py writes out/mainos_bus.bin, the image a gate or a flash just
built. fxlive rebuilds on every save, so it must not replace that file.
build_bus reads its module-level OUT when main() writes the image, so this
imports it, points OUT at the given path, and calls main(): the same build,
one path different. If build_bus stops having an OUT, this refuses rather
than let the build land on the shared path.
"""
import os
import pathlib
import sys

out = pathlib.Path(sys.argv[1]).resolve()
root = pathlib.Path.cwd()
if not (root / "tools/build/build_bus.py").is_file():
    sys.exit("build_image.py: run from an octabam checkout")
sys.argv = [str(root / "tools/build/build_bus.py")]
sys.path.insert(0, str(root / "tools/build"))
import build_bus  # noqa: E402

if not isinstance(getattr(build_bus, "OUT", None), pathlib.Path):
    sys.exit("build_image.py: build_bus.py has no OUT path any more; fxlive needs updating "
             "(refusing to build to out/mainos_bus.bin)")
if os.environ.get("DEV") or os.environ.get("MODE") or os.environ.get("DELAYPROBE"):
    sys.exit("build_image.py: DEV, MODE and DELAYPROBE builds choose their own path; unset them")
build_bus.OUT = out
build_bus.main()
