"""Install the complete Instagram skill bundle without overwriting user files."""
import argparse
import os
from pathlib import Path
import shutil


def install(codex_home):
    source = Path(__file__).resolve().parent / "skills"
    skills = sorted(source.glob("ig-*"))
    destination = Path(codex_home).expanduser().resolve() / "skills"
    conflicts = [p.name for p in skills if (destination / p.name).exists()]
    if conflicts:
        raise FileExistsError("Existing skills: " + ", ".join(conflicts))
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, destination / skill.name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=os.environ.get(
        "CODEX_HOME", str(Path.home() / ".codex")))
    args = parser.parse_args()
    try:
        print(f"Installed Instagram skills to {install(args.codex_home)}")
    except (OSError, shutil.Error) as exc:
        parser.exit(1, f"Installation failed: {exc}\n")
