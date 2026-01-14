from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _import_lib() -> object:
    build_root = Path(__file__).resolve().parent.parent
    scripts_dir = build_root / "Scripts"
    sys.path.insert(0, str(scripts_dir))
    import uebuildlib  # type: ignore

    return uebuildlib


def _copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def cmd_init(args: argparse.Namespace) -> int:
    uebuildlib = _import_lib()
    build_root = Path(__file__).resolve().parent.parent
    config_path = Path(args.config_path).expanduser().resolve() if args.config_path else uebuildlib.default_config_path(build_root)

    template = build_root / "Templates" / "BuildConfig.template.json"
    if not template.exists():
        print(f"[error] Missing template: {template}")
        return 2

    if config_path.exists() and not args.force:
        print(f"[ok] Config exists: {config_path}")
        return 0

    config_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, config_path)
    print(f"[ok] Wrote config: {config_path}")
    print("[next] Edit BuildConfig.json and run: uebuild doctor")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    uebuildlib = _import_lib()
    build_root = Path(__file__).resolve().parent.parent
    project_root = uebuildlib.get_project_root(build_root)
    config_path = Path(args.config_path).expanduser().resolve() if args.config_path else uebuildlib.default_config_path(build_root)

    ok = True

    print(f"[info] ProjectRoot: {project_root}")
    print(f"[info] BuildRoot:   {build_root}")
    print(f"[info] ConfigPath:  {config_path}")

    try:
        cfg = uebuildlib.read_json(config_path)
    except Exception as exc:
        print(f"[error] {exc}")
        return 2

    result = uebuildlib.validate_config(cfg, config_path=config_path)
    for w in result.warnings:
        print(f"[warn] {w}")
    for e in result.errors:
        ok = False
        print(f"[error] {e}")

    if ok:
        print("[ok] doctor passed")
        return 0
    return 2


def cmd_build(args: argparse.Namespace) -> int:
    uebuildlib = _import_lib()
    build_root = Path(__file__).resolve().parent.parent
    project_root = uebuildlib.get_project_root(build_root)
    config_path = Path(args.config_path).expanduser().resolve() if args.config_path else uebuildlib.default_config_path(build_root)

    cfg = uebuildlib.read_json(config_path)
    result = uebuildlib.validate_config(cfg, config_path=config_path)
    for w in result.warnings:
        print(f"[warn] {w}")
    if not result.ok:
        for e in result.errors:
            print(f"[error] {e}")
        return 2

    cmd, env = uebuildlib.build_uat_command(
        cfg=cfg,
        config_path=config_path,
        platform=args.platform,
        build_config=args.config,
        extra_uat_args=args.extra_uat_arg,
    )

    hooks_dir = build_root / "Hooks"
    rc = uebuildlib.run_hook("PreBuild", hooks_dir=hooks_dir, env=env, dry_run=args.dry_run)
    if rc != 0:
        return rc

    rc = uebuildlib.run(cmd, cwd=project_root, env=env, dry_run=args.dry_run)
    if rc != 0:
        return rc

    return uebuildlib.run_hook("PostBuild", hooks_dir=hooks_dir, env=env, dry_run=args.dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(prog="uebuild", description="UE5 Build SDK CLI")
    parser.add_argument("--config-path", default=None, help="Override BuildConfig.json path")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create BuildConfig.json from template")
    p_init.add_argument("--force", action="store_true", help="Overwrite if exists")
    p_init.set_defaults(func=cmd_init)

    p_doc = sub.add_parser("doctor", help="Validate config and environment")
    p_doc.set_defaults(func=cmd_doctor)

    p_build = sub.add_parser("build", help="Run UAT BuildCookRun")
    p_build.add_argument("--platform", required=True, help="Win64 / Android / IOS")
    p_build.add_argument("--config", default="Development", help="Development / Shipping / etc")
    p_build.add_argument("--dry-run", action="store_true", help="Print command without executing")
    p_build.add_argument("--extra-uat-arg", action="append", default=[], help="Append extra UAT args (repeatable)")
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
