# macOS 构建机（iOS 打包机）配置指南

目标：用于 iOS 的远端链接与签名（Windows 发起机负责 Cook/编译的部分；最终链接/签名在 Mac 完成）。

## 机器要求

- macOS（推荐最新稳定版本）
- Xcode（与项目 iOS SDK 兼容）
- Xcode Command Line Tools
- SSH 可从 Windows 发起机访问
- `rsync`（用于增量同步；macOS 自带版本较旧时可用 Homebrew 更新）

## 一键检查（本仓库提供）

在业务项目的 Mac 环境中（如果也拉取了项目代码），执行：

`chmod +x Build/Tools/setup_env_macos.sh Build/Tools/uebuild.sh && Build/Tools/setup_env_macos.sh`

该脚本不会自动导入证书/密钥，只做检查与提示。

## 需要你手动准备的内容（建议由项目组/中台规范化）

- 证书、Provisioning Profile
- Keychain 配置（非交互式签名所需）
- Xcode 首次启动/同意协议（CI 机器上常见坑）

## Windows 侧配置（BuildConfig.json 中的 iOS 字段）

`Platforms.IOS.RemoteServer` / `RemoteUser` / `SshKeyPath` 用于记录远端信息，方便团队统一配置；不同 UE 版本下 UAT/RemoteToolchain 参数可能略有差异，建议通过 `UAT.ExtraArgs`（或 `Platforms.IOS.ExtraUATArgs`）补充真实使用的参数（SDK 默认不会“猜测”并自动拼接 iOS 远端参数）。
