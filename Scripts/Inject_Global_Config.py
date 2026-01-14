from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import uebuildlib


def _is_windows() -> bool:
    return os.name == "nt"


def _buildconfiguration_xml_path() -> Path:
    if _is_windows():
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not set")
        return Path(appdata) / "Unreal Engine" / "UnrealBuildTool" / "BuildConfiguration.xml"

    # UE uses per-user config paths on macOS/Linux too, but UBA is Windows-only in most setups.
    # Keep this best-effort for parity; script will no-op by default on non-Windows.
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "Epic" / "UnrealBuildTool" / "BuildConfiguration.xml"
    return home / ".config" / "Epic" / "UnrealBuildTool" / "BuildConfiguration.xml"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _ns(tag: str) -> str:
    return f"{{https://www.unrealengine.com/BuildConfiguration}}{tag}"


def _load_or_create_tree(path: Path) -> ET.ElementTree:
    if path.exists():
        return ET.parse(path)

    root = ET.Element(_ns("Configuration"))
    return ET.ElementTree(element=root)


def _find_or_create(parent: ET.Element, tag: str) -> ET.Element:
    for child in parent:
        if child.tag == tag:
            return child
    child = ET.SubElement(parent, tag)
    return child


def _set_text(elem: ET.Element, value: str) -> None:
    elem.text = value


def inject_uba_coordinator(*, coordinator_ip: str, path: Path) -> None:
    _ensure_parent(path)
    tree = _load_or_create_tree(path)
    root = tree.getroot()

    # Support both namespaced and non-namespaced existing XMLs.
    if root.tag.endswith("Configuration"):
        use_ns = root.tag.startswith("{")
    else:
        use_ns = True

    def tag(name: str) -> str:
        return _ns(name) if use_ns else name

    uba = _find_or_create(root, tag("UnrealBuildAccelerator"))
    coordinator = _find_or_create(uba, tag("Coordinator"))
    _set_text(coordinator, coordinator_ip)

    # Pretty-ish formatting (ElementTree doesn't indent by default)
    try:
        ET.indent(tree, space="  ", level=0)  # py3.9+
    except Exception:
        pass

    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject UBA coordinator into UBT BuildConfiguration.xml")
    parser.add_argument(
        "--config-path",
        default=None,
        help="Path to BuildConfig.json (default: <Project>/Config/BuildSystem/BuildConfig.json)",
    )
    parser.add_argument(
        "--force-non-windows",
        action="store_true",
        help="Allow writing BuildConfiguration.xml on non-Windows (UBA is typically Windows-only).",
    )
    args = parser.parse_args()

    build_root = uebuildlib.get_build_root(Path(__file__))
    config_path = Path(args.config_path).expanduser().resolve() if args.config_path else uebuildlib.default_config_path(build_root)

    cfg = uebuildlib.read_json(config_path)
    uba = cfg.get("UBA", {}) if isinstance(cfg.get("UBA"), dict) else {}
    enabled = bool(uba.get("Enabled", False))
    coordinator_ip = uba.get("CoordinatorIP")

    if not enabled:
        print("[info] UBA is disabled in config; nothing to inject.")
        return 0

    if not isinstance(coordinator_ip, str) or not coordinator_ip.strip():
        print("[error] UBA.Enabled is true but UBA.CoordinatorIP is missing.")
        return 2

    if not _is_windows() and not args.force_non_windows:
        print("[info] Host is non-Windows; skip injection (use --force-non-windows to override).")
        return 0

    xml_path = _buildconfiguration_xml_path()
    inject_uba_coordinator(coordinator_ip=coordinator_ip.strip(), path=xml_path)
    print(f"[ok] Updated: {xml_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

