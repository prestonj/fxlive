"""Where the octabam checkout fxlive runs against is, and what fxlive builds in it.

fxlive keeps none of octabam's code: it imports the remixer (registry,
schema, send_probe) from a checkout, builds that checkout's remixes, and
compiles its two hosts from that checkout's sources. Any checkout works,
including a worktree with a module branch in it, which is the point.

The checkout is, first match:
  1. $OCTABAM;
  2. the directory you run from, or one above it, that holds tools/remix/schema.py;
  3. ../octabam beside this repository.

Everything fxlive writes goes under the checkout's out/fxlive/ (gitignored
there): the images, the dumps, and build/, the two hosts. So a worktree's
hosts are built from that worktree's sources, never another's.
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def _is_octabam(d):
    return (d / "tools/remix/schema.py").is_file() and (d / "tools/build/build_bus.py").is_file()


def find():
    env = os.environ.get("OCTABAM")
    if env:
        d = pathlib.Path(env).expanduser().resolve()
        if not _is_octabam(d):
            sys.exit(f"fxlive: OCTABAM={env} is not an octabam checkout (no tools/remix/schema.py)")
        return d
    for d in (pathlib.Path.cwd().resolve(), *pathlib.Path.cwd().resolve().parents):
        if _is_octabam(d):
            return d
    d = (HERE.parent / "octabam").resolve()
    if _is_octabam(d):
        return d
    sys.exit("fxlive: no octabam checkout found: run from inside one, or set OCTABAM=<path>")


ROOT = find()
OUTDIR = ROOT / "out/fxlive"
BUILD = OUTDIR / "build"                 # CMakeLists.txt here, configured by the Makefile
DSP_HOST = BUILD / "dsp_host_stream"     # the checkout's dsp_host.cpp + patches/dsp_host-stream.patch
CF_HOST = BUILD / "ot_cf_host"           # cf_host.cpp linked against the checkout's ot_machine

# octabam's tools import each other through tools/toolpath.py
sys.path.insert(0, str(ROOT / "tools"))
import toolpath  # noqa: E402,F401


def build_image(remix, image, env=None):
    """Build `remix` to `image`, never out/mainos_bus.bin. Returns the
    CompletedProcess (stdout, stderr, returncode) as running build_bus.py would."""
    import subprocess
    env = dict(env or os.environ, REMIX=remix, XBUS="1", SPEC="1")
    return subprocess.run([sys.executable, str(HERE / "build_image.py"), str(image)],
                          cwd=ROOT, env=env, capture_output=True, text=True)
