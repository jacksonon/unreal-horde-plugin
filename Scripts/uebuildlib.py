from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_windows() -> bool:
    return os.name == "nt"


def get_build_root(current_file: Path) -> Path:
    current_file = current_file.resolve()
    if current_file.parent.name in {"Scripts", "Tools", "Templates", "Hooks", "Docs", "Extras"}:
        return current_file.parent.parent
    return current_file.parent


def get_project_root(build_root: Path) -> Path:
    return build_root.resolve().parent


def default_config_path(build_root: Path) -> Path:
    project_root = get_project_root(build_root)
    return project_root / "Config" / "BuildSystem" / "BuildConfig.json"


def read_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"Config not found: {path}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON: {path} ({exc})") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Top-level JSON must be an object: {path}")
    return data


def find_uproject(project_root: Path, project_name: str | None) -> Path:
    if project_name:
        candidate = project_root / f"{project_name}.uproject"
        if candidate.exists():
            return candidate

    uprojects = sorted(project_root.glob("*.uproject"))
    if len(uprojects) == 1:
        return uprojects[0]
    if len(uprojects) > 1:
        raise ConfigError(
            "Multiple .uproject files found; set ProjectName in BuildConfig.json: "
            + ", ".join(p.name for p in uprojects)
        )
    raise ConfigError(f"No .uproject file found under {project_root}")


def uat_path(engine_root: Path) -> Path:
    if _is_windows():
        return engine_root / "Engine" / "Build" / "BatchFiles" / "RunUAT.bat"
    return engine_root / "Engine" / "Build" / "BatchFiles" / "RunUAT.sh"


def format_cmd(cmd: list[str]) -> str:
    def q(s: str) -> str:
        if any(c.isspace() for c in s) or '"' in s:
            return '"' + s.replace('"', '\\"') + '"'
        return s

    return " ".join(q(x) for x in cmd)


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> int:
    actual_cmd = cmd
    if _is_windows() and cmd:
        first = cmd[0].lower()
        if first.endswith(".bat") or first.endswith(".cmd"):
            actual_cmd = ["cmd.exe", "/c", *cmd]

    print(format_cmd(actual_cmd))
    if dry_run:
        return 0
    completed = subprocess.run(actual_cmd, cwd=str(cwd) if cwd else None, env=env)
    return int(completed.returncode)


def run_hook(
    stage_name: str,
    *,
    hooks_dir: Path,
    env: dict[str, str] | None,
    dry_run: bool,
) -> int:
    hook_script = hooks_dir / f"{stage_name}.py"
    if not hook_script.exists():
        return 0
    cmd = [sys.executable, str(hook_script)]
    return run(cmd, cwd=hooks_dir, env=env, dry_run=dry_run)


def _bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    return default


def _get_dict(d: dict[str, Any], key: str) -> dict[str, Any]:
    v = d.get(key, {})
    return v if isinstance(v, dict) else {}


def validate_config(cfg: dict[str, Any], *, config_path: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    engine_root = cfg.get("EngineRoot")
    if not isinstance(engine_root, str) or not engine_root.strip():
        errors.append("EngineRoot is required (string)")
    else:
        p = Path(engine_root)
        if not p.exists():
            errors.append(f"EngineRoot does not exist: {engine_root}")
        else:
            uat = uat_path(p)
            if not uat.exists():
                errors.append(f"RunUAT not found under EngineRoot: {uat}")

    project_name = cfg.get("ProjectName")
    if project_name is not None and not isinstance(project_name, str):
        errors.append("ProjectName must be a string if provided")

    uba = _get_dict(cfg, "UBA")
    if _bool(uba.get("Enabled"), False):
        coord = uba.get("CoordinatorIP")
        if not isinstance(coord, str) or not coord.strip():
            errors.append("UBA.Enabled is true but UBA.CoordinatorIP is missing")
        if not _is_windows():
            warnings.append("UBA is typically Windows-only; current host is non-Windows")

    platforms = _get_dict(cfg, "Platforms")
    if not platforms:
        warnings.append("Platforms is empty; build will still work but per-platform settings are unavailable")

    uat_conf = _get_dict(cfg, "UAT")
    extra_args = uat_conf.get("ExtraArgs", [])
    if extra_args is not None and not isinstance(extra_args, list):
        errors.append("UAT.ExtraArgs must be an array of strings")

    if errors:
        errors = [f"{config_path}: {e}" for e in errors]
    if warnings:
        warnings = [f"{config_path}: {w}" for w in warnings]
    return ValidationResult(errors=errors, warnings=warnings)


def merged_uat_extra_args(cfg: dict[str, Any], extra_args: Iterable[str]) -> list[str]:
    uat_conf = _get_dict(cfg, "UAT")
    base = uat_conf.get("ExtraArgs", [])
    if not isinstance(base, list):
        base = []
    merged: list[str] = []
    for item in base:
        if isinstance(item, str) and item.strip():
            merged.append(item)
    for item in extra_args:
        if item.strip():
            merged.append(item)
    return merged


def buildcookrun_flags(cfg: dict[str, Any]) -> list[str]:
    uat_conf = _get_dict(cfg, "UAT")
    bcr = _get_dict(uat_conf, "BuildCookRun")
    flags: list[str] = []
    if _bool(bcr.get("Cook"), True):
        flags.append("-cook")
    if _bool(bcr.get("Stage"), True):
        flags.append("-stage")
    if _bool(bcr.get("Package"), True):
        flags.append("-package")
    if _bool(bcr.get("Archive"), True):
        flags.append("-archive")
    if _bool(bcr.get("Pak"), True):
        flags.append("-pak")
    return flags


def platform_uat_args(cfg: dict[str, Any], platform: str) -> list[str]:
    platforms = _get_dict(cfg, "Platforms")
    platform_cfg = _get_dict(platforms, platform)

    # Keep this conservative: many remote/iOS flags are UE-version-specific.
    # Use ExtraUATArgs in config for anything special.
    args: list[str] = []

    if platform.upper() in {"WIN64", "WINDOWS"}:
        args.append("-platform=Win64")
    elif platform.upper() == "ANDROID":
        args.append("-platform=Android")
    elif platform.upper() in {"IOS", "IOSSIMULATOR"}:
        args.append("-platform=IOS")
    else:
        args.append(f"-platform={platform}")

    extra = platform_cfg.get("ExtraUATArgs", [])
    if isinstance(extra, list):
        args.extend([x for x in extra if isinstance(x, str) and x.strip()])
    return args


def build_uat_command(
    *,
    cfg: dict[str, Any],
    config_path: Path,
    platform: str,
    build_config: str,
    extra_uat_args: Iterable[str],
) -> tuple[list[str], dict[str, str]]:
    engine_root = Path(str(cfg["EngineRoot"]))
    uat = uat_path(engine_root)

    # Prefer deriving ProjectRoot from config path when it matches the standard layout:
    # <ProjectRoot>/Config/BuildSystem/BuildConfig.json
    if config_path.parent.name == "BuildSystem" and config_path.parent.parent.name == "Config":
        project_root = config_path.parent.parent.parent.resolve()
    else:
        # Fallback to deriving from this SDK's location (expects <ProjectRoot>/Build/...)
        build_root_from_lib = get_build_root(Path(__file__))
        project_root = get_project_root(build_root_from_lib)

    project_name = cfg.get("ProjectName") if isinstance(cfg.get("ProjectName"), str) else None
    project_file = find_uproject(project_root, project_name)

    artifacts_dir = cfg.get("ArtifactsDir") if isinstance(cfg.get("ArtifactsDir"), str) else ""
    archive_dir = artifacts_dir.strip() or str(project_root / "Saved" / "BuildArtifacts")
    archive_dir = str(Path(archive_dir) / platform)

    cmd: list[str] = [
        str(uat),
        "BuildCookRun",
        f"-project={project_file}",
        "-noP4",
        "-build",
        f"-clientconfig={build_config}",
        f"-archivedirectory={archive_dir}",
    ]

    cmd.extend(buildcookrun_flags(cfg))
    cmd.extend(platform_uat_args(cfg, platform))

    uba = _get_dict(cfg, "UBA")
    if _bool(uba.get("Enabled"), False):
        cmd.extend(["-distributed", "-uba"])

    cmd.extend(merged_uat_extra_args(cfg, extra_uat_args))

    env = dict(os.environ)
    shared_ddc = cfg.get("SharedDDC") if isinstance(cfg.get("SharedDDC"), str) else None
    if shared_ddc and shared_ddc.strip():
        env["UE-SharedDataCachePath"] = shared_ddc
        env["UE_SHARED_DDC"] = shared_ddc

    env["UE_BUILD_CONFIG_PATH"] = str(config_path)
    return cmd, env
