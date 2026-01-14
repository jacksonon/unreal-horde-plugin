# Windows 发起机（CI Runner）配置指南

目标：这台 Windows 机器只负责“发起构建”。分布式编译算力由中台 UBA Farm 提供。

## 机器要求

- Windows 10/11 或 Windows Server（推荐 16GB+ RAM、SSD）
- Python 3.x（确保 `python` 在 PATH）
- 已安装 UE（与项目版本一致），并填写 `EngineRoot`
- 网络可访问：
  - 中台 UBA Coordinator（`UBA.CoordinatorIP`）
  - 共享 DDC（如 NAS）与产物归档目录（Artifacts）

## 接入步骤（业务项目）

1) 在项目根目录添加本仓库为 `Build/`：

`git submodule add <your_repo_url> Build`

2) 运行一键初始化（首次必做）：

- 双击 `Build/Tools/setup_env_windows.bat`

它会做三件事：
- 生成 `Config/BuildSystem/BuildConfig.json`（如果不存在）
- 从 `BuildConfig.json` 读取 `UBA.CoordinatorIP` 并写入本机 UBT 全局配置 `BuildConfiguration.xml`
- 执行 `uebuild doctor` 做基本自检

也可以用 CLI 生成配置（适合 CI 镜像/自动化场景）：

`Build/Tools/uebuild.cmd init`

3) 编辑配置：

`Config/BuildSystem/BuildConfig.json`

最少需要：
- `ProjectName`
- `EngineRoot`
- `UBA.Enabled` / `UBA.CoordinatorIP`
- `ArtifactsDir`（建议指向共享目录）

4) 发起构建（本地或 CI）：

`Build/Tools/uebuild.cmd build --platform Win64 --config Development`

## CI 示例（Jenkins）

```groovy
stage('Build Win64') {
  steps {
    bat 'Build\\Tools\\uebuild.cmd doctor'
    bat 'Build\\Tools\\uebuild.cmd build --platform Win64 --config Shipping'
  }
}
```

## 常见问题

- `RunUAT not found`：检查 `EngineRoot` 是否指向 UE 根目录（应包含 `Engine/Build/BatchFiles/RunUAT.bat`）。
- UBA 不生效：确认 `Build/Tools/setup_env_windows.bat` 已运行过，并检查 `%APPDATA%\\Unreal Engine\\UnrealBuildTool\\BuildConfiguration.xml` 是否包含 Coordinator。

## iOS 远端（可选）

如果你要在 Windows 发起 iOS 构建（远端 Mac 负责链接/签名），通常还需要：

- Windows → Mac 的 SSH 免密登录（`Platforms.IOS.SshKeyPath` 记录密钥路径）
- `rsync`（用于增量同步；不同 UE 版本/工具链实现不同）

SDK 默认不会“猜测”并自动拼 iOS Remote 参数；请在 `Platforms.IOS.ExtraUATArgs` 或 `UAT.ExtraArgs` 中按你们的 UE 版本加入真实可用的参数。
