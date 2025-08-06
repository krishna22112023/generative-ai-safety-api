import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

# Python ≥3.11 ships ``tomllib`` in std-lib
try:
    import tomllib  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover – sanity-check for very old Pythons
    subprocess.run([sys.executable, "-m", "pip", "install", "tomli"], check=True)
    import tomli as tomllib  # type: ignore

from setuptools import setup  # type: ignore
from setuptools.command.develop import develop  # type: ignore

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def ensure_uv_installed() -> None:
    """Install the *uv* package-manager if it is not already available."""
    if shutil.which("uv") is None:
        print("[setup] 'uv' was not found – installing it with pip …")
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
    else:
        print("[setup] 'uv' already present – skipping installation.")


def ensure_venv() -> Path:
    """Create a local `.venv` in the project root if it does not yet exist."""
    root = Path(__file__).parent.resolve()
    venv_dir = root / ".venv"
    if venv_dir.exists():
        print(f"[setup] Re-using existing virtual-env at {venv_dir}")
        return venv_dir

    print(f"[setup] Creating virtual-env at {venv_dir} …")
    venv.create(venv_dir, with_pip=True, symlinks=True, clear=False)
    return venv_dir


def uv_bin(venv_dir: Path) -> str:
    """Return the *uv* executable inside *venv_dir* (fall back to global)."""
    bin_sub = "Scripts" if os.name == "nt" else "bin"
    candidate = venv_dir / bin_sub / "uv"
    return str(candidate) if candidate.exists() else "uv"


def install_project_deps(uv_exe: str) -> None:
    """Install runtime dependencies listed in *pyproject.toml* using *uv*."""
    print("[setup] Installing dependencies from pyproject.toml …")
    with open("pyproject.toml", "rb") as fp:
        pyproject = tomllib.load(fp)
    deps = pyproject.get("project", {}).get("dependencies", [])
    if not deps:
        print("[setup] No dependencies declared – skipping.")
        return

    subprocess.run([uv_exe, "pip", "install", *deps], check=True)


def install_guardrail_validators(uv_exe: str) -> None:
    """Install default Guardrails Hub validators using *uv*."""
    validators = [
        "hub://guardrails/toxic_language",
        "hub://guardrails/guardrails_pii",
        "hub://guardrails/secrets_present",
    ]
    print("[setup] Installing Guardrails validators …")
    for v in validators:
        subprocess.run([uv_exe, "run", "guardrails", "hub", "install", v], check=True)


def run_alembic_migrations(uv_exe: str) -> None:
    """Run Alembic migrations to prepare the database schema."""
    print("[setup] Running Alembic migrations …")
    # Ensure we are in the project root where *alembic.ini* resides.
    subprocess.run([uv_exe, "run", "alembic", "upgrade", "head"], check=True)


# ---------------------------------------------------------------------------
# Custom develop command that triggers the bootstrap logic above
# ---------------------------------------------------------------------------

class BootstrapDevelop(develop):
    """`pip install -e .` entry-point – bootstraps local dev environment."""

    def run(self):  # noqa: D401 – imperative style is fine
        # first, perform standard setuptools develop install (creates .pth etc.)
        super().run()

        # then, execute custom bootstrap steps
        print("[setup] Boot-strapping development environment …")
        ensure_uv_installed()
        venv_dir = ensure_venv()
        uv_exe = uv_bin(venv_dir)
        install_project_deps(uv_exe)
        install_guardrail_validators(uv_exe)
        run_alembic_migrations(uv_exe)
        print("[setup] All done – environment ready! 🎉")


# ---------------------------------------------------------------------------
# Minimal metadata – actual packaging info lives in *pyproject.toml*
# ---------------------------------------------------------------------------

setup(
    name="generative-ai-safety-api-bootstrap",
    version="0.0.0",  # dummy – real version in pyproject.toml
    description="Bootstrap helper so `pip install -e .` prepares dev env.",
    cmdclass={"develop": BootstrapDevelop},
)
