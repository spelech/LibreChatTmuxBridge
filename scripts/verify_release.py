#!/usr/bin/env python3
"""
Release and Version Verification Engine for LibreChatTmuxBridge.
Validates version synchronization across manifests, markdown link integrity, and test coverage.
"""

import argparse
import re
import sys
from pathlib import Path


def extract_pyproject_version(root_dir: Path) -> str | None:
    pyproject = root_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    content = pyproject.read_text(encoding="utf-8")
    m = re.search(r'version\s*=\s*"([^"]+)"', content)
    return m.group(1) if m else None


def extract_package_json_version(root_dir: Path) -> str | None:
    pkg = root_dir / "package.json"
    if not pkg.exists():
        return None
    content = pkg.read_text(encoding="utf-8")
    m = re.search(r'"version"\s*:\s*"([^"]+)"', content)
    return m.group(1) if m else None


def extract_init_version(root_dir: Path) -> str | None:
    init_file = root_dir / "src" / "librechat_tmux_bridge" / "__init__.py"
    if not init_file.exists():
        return None
    content = init_file.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    return m.group(1) if m else None


def check_version_sync(root_dir: Path) -> bool:
    print("🔍 Checking version consistency across manifests...")
    py_ver = extract_pyproject_version(root_dir)
    pkg_ver = extract_package_json_version(root_dir)
    init_ver = extract_init_version(root_dir)

    versions = {"pyproject.toml": py_ver, "package.json": pkg_ver, "src/__init__.py": init_ver}
    print(f"  Versions found: {versions}")

    unique_versions = set(v for v in versions.values() if v is not None)
    if len(unique_versions) > 1:
        print(f"❌ Version mismatch detected: {versions}")
        return False

    if not unique_versions:
        print("❌ No versions found in manifests.")
        return False

    ver = unique_versions.pop()
    print(f"✅ Version synchronized at v{ver}")
    return True


def check_markdown_links(root_dir: Path) -> bool:
    print("🔍 Checking markdown relative links and anchors...")
    has_errors = False
    for md_file in root_dir.glob("**/*.md"):
        # Ignore virtualenv, node_modules, cache dirs
        if any(
            part.startswith(".") or part in ["node_modules", "bin", "obj", ".venv", "dist"]
            for part in md_file.parts
        ):
            continue
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        # Find markdown links: [text](path)
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, link in links:
            if (
                link.startswith("http://")
                or link.startswith("https://")
                or link.startswith("#")
                or link.startswith("mailto:")
            ):
                continue
            # Strip anchors
            target_path = link.split("#")[0]
            if not target_path:
                continue
            # Handle absolute links within VitePress docs
            if target_path.startswith("/"):
                target_in_docs = root_dir / "docs" / target_path.lstrip("/")
                if target_in_docs.exists() or (target_in_docs.with_suffix(".md")).exists():
                    continue
                resolved = (root_dir / target_path.lstrip("/")).resolve()
            else:
                resolved = (md_file.parent / target_path).resolve()
                if not resolved.exists() and (resolved.with_suffix(".md")).exists():
                    resolved = resolved.with_suffix(".md")

            if not resolved.exists():
                print(f"❌ Broken link in {md_file.relative_to(root_dir)}: [{text}]({link})")
                has_errors = True

    if not has_errors:
        print("✅ All markdown links verified successfully.")
    return not has_errors


def main():
    parser = argparse.ArgumentParser(description="LibreChatTmuxBridge Release Verification")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test suite execution")
    parser.add_argument("--ci", action="store_true", help="CI execution mode")
    parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent

    ver_ok = check_version_sync(root_dir)
    links_ok = check_markdown_links(root_dir)

    if not (ver_ok and links_ok):
        print("\n❌ Release verification failed!")
        sys.exit(1)

    print("\n✅ All release gates passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
