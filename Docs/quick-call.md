# 快速调用（复制即用）

## Windows（本地/CI）

```bat
REM 1) 初始化（首次）
Build\Tools\setup_env_windows.bat

REM 2) 自检
Build\Tools\uebuild.cmd doctor

REM 3) 构建（示例：Win64 Shipping）
Build\Tools\uebuild.cmd build --platform Win64 --config Shipping
```

## macOS（本地/CI）

```bash
chmod +x Build/Tools/uebuild.sh
Build/Tools/uebuild.sh doctor
Build/Tools/uebuild.sh build --platform IOS --config Shipping --dry-run
```

## Jenkins 示例

```groovy
stage('Doctor') {
  steps { bat 'Build\\Tools\\uebuild.cmd doctor' }
}
stage('Build Win64') {
  steps { bat 'Build\\Tools\\uebuild.cmd build --platform Win64 --config Shipping' }
}
```

## GitLab CI 示例

```yaml
build_win64:
  stage: build
  tags: [windows]
  script:
    - Build\Tools\uebuild.cmd doctor
    - Build\Tools\uebuild.cmd build --platform Win64 --config Shipping
```

