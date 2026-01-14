# UE5 分布式构建 SDK（Build 包 + CLI + 可选插件）

目标：把 UE5 分布式构建能力打包成“配置即用”的 SDK，业务线只需要把本仓库作为 Submodule 放到项目根目录的 `Build/`，填一次配置，即可在 CI 上快速发起 Win64/Android/iOS 构建。

## 目录结构（放到业务项目后）

```
MyGame/
├── Build/                # 本仓库（Submodule）
│   ├── Scripts/          # Python 脚本（核心逻辑）
│   ├── Tools/            # 一键初始化、CLI wrapper
│   ├── Templates/        # 配置模板
│   ├── Hooks/            # 预留 Hook（可选）
│   ├── Docs/             # 配置文档
│   └── Extras/           # 可选 UE 插件等
├── Config/
│   └── BuildSystem/
│       └── BuildConfig.json
├── MyGame.uproject
└── Source/
```

## 快速开始（Windows 发起机）

1) 引入（建议作为 Submodule）：

`git submodule add <your_repo_url> Build`

2) 初始化（生成配置 + 注入 UBT 全局配置）：

- 双击运行 `Build/Tools/setup_env_windows.bat`（或执行 `Build/Tools/setup_env_windows.ps1`）

3) 编辑 `Config/BuildSystem/BuildConfig.json`

4) 运行自检：

`Build/Tools/uebuild.cmd doctor`

5) 发起构建：

`Build/Tools/uebuild.cmd build --platform Win64 --config Development`

## 文档

- `Docs/windows-machine-setup.md`
- `Docs/macos-machine-setup.md`
- `Docs/quick-call.md`
- `Docs/buildconfig-reference.md`

## 可选：安装 UE 插件

- Windows：`Build/Tools/install_ue_plugin_windows.bat`
- macOS：`chmod +x Build/Tools/install_ue_plugin_macos.sh && Build/Tools/install_ue_plugin_macos.sh`
