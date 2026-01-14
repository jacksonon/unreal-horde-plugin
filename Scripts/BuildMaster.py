from __future__ import annotations

import argparse
from pathlib import Path

import uebuildlib


def main() -> int:
    parser = argparse.ArgumentParser(description="UE5 Build SDK - BuildMaster (compat entrypoint)")
    parser.add_argument("--platform", required=True, help="Win64 / Android / IOS")
    parser.add_argument("--config", default="Development", help="Development / Shipping / etc")
    parser.add_argument(
        "--config-path",
        default=None,
        help="Path to BuildConfig.json (default: <Project>/Config/BuildSystem/BuildConfig.json)",
    )
    parser.add_argument(
        "--json_config",
        default=None,
        help="Alias of --config-path (compat with older docs).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print UAT command without executing")
    parser.add_argument(
        "--extra-uat-arg",
        action="append",
        default=[],
        help="Append additional UAT args (repeatable). Prefer UAT.ExtraArgs in JSON for shared defaults.",
    )
    args = parser.parse_args()

    build_root = uebuildlib.get_build_root(Path(__file__))
    override = args.config_path or args.json_config
    config_path = Path(override).expanduser().resolve() if override else uebuildlib.default_config_path(build_root)

    cfg = uebuildlib.read_json(config_path)
    result = uebuildlib.validate_config(cfg, config_path=config_path)
    for w in result.warnings:
        print(f"[warn] {w}")
    if not result.ok:
        for e in result.errors:
            print(f"[error] {e}")
        return 2

    hooks_dir = build_root / "Hooks"

    cmd, env = uebuildlib.build_uat_command(
        cfg=cfg,
        config_path=config_path,
        platform=args.platform,
        build_config=args.config,
        extra_uat_args=args.extra_uat_arg,
    )

    rc = uebuildlib.run_hook("PreBuild", hooks_dir=hooks_dir, env=env, dry_run=args.dry_run)
    if rc != 0:
        return rc

    rc = uebuildlib.run(cmd, cwd=uebuildlib.get_project_root(build_root), env=env, dry_run=args.dry_run)
    if rc != 0:
        return rc

    return uebuildlib.run_hook("PostBuild", hooks_dir=hooks_dir, env=env, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
