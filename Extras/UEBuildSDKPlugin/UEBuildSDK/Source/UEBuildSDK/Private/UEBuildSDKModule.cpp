#include "UEBuildSDKModule.h"

#include "HAL/PlatformProcess.h"
#include "Framework/Commands/UIAction.h"
#include "Misc/MessageDialog.h"
#include "Misc/Paths.h"
#include "Styling/SlateIcon.h"
#include "ToolMenus.h"

static FString GetProjectBuildRoot()
{
  return FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / TEXT("Build"));
}

static bool EnsureBuildToolsExist(FString& OutBuildRoot, FString& OutError)
{
  OutBuildRoot = GetProjectBuildRoot();
  const FString UebuildPath = OutBuildRoot / TEXT("Tools/uebuild.py");
  if (!FPaths::FileExists(UebuildPath))
  {
    OutError = FString::Printf(TEXT("Cannot find %s. Make sure this repo is placed at <ProjectRoot>/Build."), *UebuildPath);
    return false;
  }
  return true;
}

static void LaunchUeBuild(const FString& Args)
{
  FString BuildRoot;
  FString Error;
  if (!EnsureBuildToolsExist(BuildRoot, Error))
  {
    FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(Error));
    return;
  }

  const FString WorkingDir = FPaths::ProjectDir();
  const FString PythonExe = TEXT("python");
  const FString ScriptPath = BuildRoot / TEXT("Tools/uebuild.py");
  const FString Params = FString::Printf(TEXT("\"%s\" %s"), *ScriptPath, *Args);

  void* ReadPipe = nullptr;
  void* WritePipe = nullptr;
  FPlatformProcess::CreatePipe(ReadPipe, WritePipe);

  FProcHandle Handle = FPlatformProcess::CreateProc(*PythonExe, *Params, true, false, false, nullptr, 0, *WorkingDir, WritePipe, ReadPipe);
  if (!Handle.IsValid())
  {
    FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(TEXT("Failed to launch python. Ensure python is available in PATH.")));
  }
}

static void OpenBuildConfig()
{
  const FString ConfigPath = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / TEXT("Config/BuildSystem/BuildConfig.json"));
  if (!FPaths::FileExists(ConfigPath))
  {
    FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(TEXT("BuildConfig.json not found. Run Build/Tools/setup_env_windows or uebuild init first.")));
    return;
  }
  FPlatformProcess::LaunchFileInDefaultExternalApplication(*ConfigPath);
}

void FUEBuildSDKModule::StartupModule()
{
  if (UToolMenus::IsToolMenuUIEnabled())
  {
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FUEBuildSDKModule::RegisterMenus));
  }
}

void FUEBuildSDKModule::ShutdownModule()
{
  UnregisterMenus();
}

void FUEBuildSDKModule::RegisterMenus()
{
  FToolMenuOwnerScoped OwnerScoped(this);

  UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
  if (!Menu)
  {
    return;
  }

  FToolMenuSection& Section = Menu->AddSection("UEBuildSDK", FText::FromString("UE Build SDK"));

  Section.AddMenuEntry(
    "UEBuildSDK_OpenConfig",
    FText::FromString("Open BuildConfig.json"),
    FText::FromString("Open Config/BuildSystem/BuildConfig.json"),
    FSlateIcon(),
    FUIAction(FExecuteAction::CreateStatic(&OpenBuildConfig))
  );

  Section.AddMenuEntry(
    "UEBuildSDK_Doctor",
    FText::FromString("Run uebuild doctor"),
    FText::FromString("Validate build config and environment"),
    FSlateIcon(),
    FUIAction(FExecuteAction::CreateStatic(&LaunchUeBuild, FString(TEXT("doctor"))))
  );

  Section.AddMenuEntry(
    "UEBuildSDK_BuildWin64Dev",
    FText::FromString("Build Win64 (Development)"),
    FText::FromString("Run uebuild build --platform Win64 --config Development"),
    FSlateIcon(),
    FUIAction(FExecuteAction::CreateStatic(&LaunchUeBuild, FString(TEXT("build --platform Win64 --config Development"))))
  );
}

void FUEBuildSDKModule::UnregisterMenus()
{
  if (UToolMenus::IsAvailable())
  {
    UToolMenus::UnregisterOwner(this);
  }
}

IMPLEMENT_MODULE(FUEBuildSDKModule, UEBuildSDK)
