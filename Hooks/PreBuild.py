import os

print("[hook] PreBuild")
print(f"[hook] UE_SHARED_DDC={os.environ.get('UE_SHARED_DDC', '')}")

