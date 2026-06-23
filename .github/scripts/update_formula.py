from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMULA = ROOT / "Formula" / "trustcheck.rb"
SEMVER_TAG = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")


def run_git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def version_key(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def latest_stable_tag(upstream_path: Path) -> tuple[str, str]:
    tags = run_git(["tag", "--list", "v*"], upstream_path).splitlines()
    candidates: list[tuple[tuple[int, int, int], str, str]] = []
    for tag in tags:
        match = SEMVER_TAG.fullmatch(tag)
        if match:
            version = match.group("version")
            candidates.append((version_key(version), tag, version))
    if not candidates:
        raise SystemExit("No stable vMAJOR.MINOR.PATCH tags found in upstream repository.")
    _, tag, version = max(candidates)
    return tag, version


def pypi_sdist(version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/trustcheck/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)

    sdists = [entry for entry in data["urls"] if entry.get("packagetype") == "sdist"]
    if not sdists:
        raise SystemExit(f"No PyPI sdist found for trustcheck {version}.")

    sdist = sdists[0]
    return sdist["url"], sdist["digests"]["sha256"]


def update_formula(version: str, source_url: str, sha256: str) -> None:
    text = FORMULA.read_text(encoding="utf-8")
    text = re.sub(
        r'(?m)^  url ".+"\n  sha256 "[0-9a-f]+"',
        f'  url "{source_url}"\n  sha256 "{sha256}"',
        text,
        count=1,
    )
    text = re.sub(r'(?m)^  version ".+"', f'  version "{version}"', text, count=1)
    FORMULA.write_text(text, encoding="utf-8")


def write_github_output(tag: str, version: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"tag={tag}\n")
        output.write(f"version={version}\n")


def main() -> int:
    tag = os.environ.get("TRUSTCHECK_TAG", "").strip()
    upstream = Path(os.environ.get("UPSTREAM_PATH", ROOT / ".upstream" / "trustcheck"))

    if tag:
        match = SEMVER_TAG.fullmatch(tag)
        if not match:
            raise SystemExit(f"TRUSTCHECK_TAG must look like vMAJOR.MINOR.PATCH, got {tag!r}.")
        version = match.group("version")
    else:
        tag, version = latest_stable_tag(upstream)

    source_url, sha256 = pypi_sdist(version)
    update_formula(version, source_url, sha256)
    write_github_output(tag, version)
    print(f"Updated Formula/trustcheck.rb to {tag} from {source_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
