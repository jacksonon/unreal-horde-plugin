# UE 插件（可选）

本仓库默认按 Spec 作为 `Build/` 工具包使用；如果你还希望在 Editor 里有菜单入口，可以安装本插件。

## 安装

把 `Extras/UEBuildSDKPlugin/UEBuildSDK` 复制到业务项目的：

`<ProjectRoot>/Plugins/UEBuildSDK`

然后打开项目，在 Plugins 面板启用 `UEBuildSDK`。

## 功能

- 打开 `Config/BuildSystem/BuildConfig.json`
- 一键运行 `uebuild doctor`
- 一键运行 `uebuild build`（示例：Win64 Development）

