using UnrealBuildTool;

public class UEBuildSDK : ModuleRules
{
  public UEBuildSDK(ReadOnlyTargetRules Target) : base(Target)
  {
    PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

    PrivateDependencyModuleNames.AddRange(
      new string[]
      {
        "Core",
        "CoreUObject",
        "Engine",
        "Projects",
        "ToolMenus",
        "UnrealEd"
      }
    );
  }
}

