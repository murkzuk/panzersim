import os
import shutil

print("\n--- T-34 vs Tiger Mission Builder (Phase 1) ---\n")

# Step 1: Get install and template paths
tvt_path = input("Enter your T-34 vs Tiger installation path (e.g., M:/T34vsTiger): ").strip()
if not os.path.isdir(tvt_path):
    print("Error: Provided TvT path does not exist.")
    exit(1)

print(f"Using TvT install path: {tvt_path}\n")

template_rel_path = input("Enter the RELATIVE path to the existing mission folder (e.g., Missions/MyMission/ForwardProbe): ").strip()
template_path = os.path.join(tvt_path, template_rel_path)
if not os.path.isdir(template_path):
    print(f"Error: Template folder '{template_path}' not found.")
    exit(1)

new_mission_name = input("Enter the NEW mission name (no spaces, e.g., Murkz2025): ").strip()
parent_folder = os.path.dirname(template_path)
new_path = os.path.join(parent_folder, new_mission_name)

# Step 2: Copy folder
if os.path.exists(new_path):
    print(f"Error: Target folder '{new_path}' already exists.")
    exit(1)

print(f"\nCopying '{template_path}' to '{new_path}'...")
shutil.copytree(template_path, new_path)
print("Folder copied.\n")

# Step 3: Perform string replacement in .script/.rsr files
old_prefix = os.path.basename(template_path)
new_prefix = new_mission_name

print(f"Renaming inside files: {old_prefix} -> {new_prefix}\n")

for root, dirs, files in os.walk(new_path):
    for file in files:
        if file.endswith(".script") or file.endswith(".rsr"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="ansi", errors='replace') as f:
                content = f.read()
            content = content.replace(old_prefix, new_prefix)
            with open(path, "w", encoding="ansi", errors='replace') as f:
                f.write(content)

print("Mission scaffolding complete. Ready for metadata entry in Phase 2.")
