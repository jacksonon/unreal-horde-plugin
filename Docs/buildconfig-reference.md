# BuildConfig.json 字段说明

模板文件在：`Build/Templates/BuildConfig.template.json`

配置文件路径约定为：`<ProjectRoot>/Config/BuildSystem/BuildConfig.json`

## 顶层字段

- `ProjectName`：项目名（用于定位 `<ProjectName>.uproject`；如果项目根目录只有一个 `.uproject`，可不填）
- `EngineVersion`：仅用于记录/对齐（不参与逻辑）
- `EngineRoot`：UE 根目录（必须包含 `Engine/Build/BatchFiles/RunUAT.(bat|sh)`）
- `SharedDDC`：共享 DDC 路径（如果填写，SDK 会设置环境变量 `UE-SharedDataCachePath`）
- `ArtifactsDir`：构建产物归档目录（archive 输出会放到 `<ArtifactsDir>/<Platform>`）

## `UBA`

- `Enabled`：是否启用 UBA 参数（SDK 会向 UAT 追加 `-distributed -uba`）
- `CoordinatorIP`：中台 UBA Coordinator 地址（Windows 发起机初始化脚本会注入到本机 UBT `BuildConfiguration.xml`）

## `Platforms`

为不同平台提供额外配置；SDK 默认只做“记录 + 基础透传”，真实平台差异建议通过 `ExtraUATArgs` 完成。

- `Platforms.<Platform>.ExtraUATArgs`：数组，追加到 UAT 命令行

## `UAT`

- `ExtraArgs`：数组，所有平台都会追加到 UAT 命令行（适合团队统一默认值）
- `BuildCookRun`：开关组合（Cook/Stage/Package/Archive/Pak）

