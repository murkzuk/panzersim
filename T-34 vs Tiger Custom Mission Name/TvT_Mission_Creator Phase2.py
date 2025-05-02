import os
import shutil

print("--- T-34 vs Tiger Mission Builder ---\n")

# Get installation path
tvt_path = input("Enter your T-34 vs Tiger installation path (e.g., M:/T34vsTiger): ").strip()
if not os.path.isdir(tvt_path):
    print("Error: TvT path not found.")
    exit(1)
print(f"Using TvT install path: {tvt_path}")

# Get source mission folder
existing_rel = input("Enter the RELATIVE path to the existing mission folder (e.g., Missions/MyMission/ForwardProbe): ").strip()
existing_folder = os.path.join(tvt_path, existing_rel)
if not os.path.isdir(existing_folder):
    print(f"Error: Folder '{existing_folder}' not found.")
    exit(1)

# Get new mission name
new_mission_name = input("Enter the NEW mission name (no spaces, e.g., Murkz2025): ").strip()
parent_folder = os.path.dirname(existing_folder)
new_folder = os.path.join(parent_folder, new_mission_name)

if os.path.exists(new_folder):
    print(f"Error: Target folder '{new_folder}' already exists.")
    exit(1)

# Copy the folder
print(f"\nCopying '{existing_folder}' to '{new_folder}'...")
shutil.copytree(existing_folder, new_folder)
print("Folder copied.")

# Rename content inside .script files
old_class_prefix = os.path.basename(existing_folder)
new_class_prefix = new_mission_name
print(f"\nRenaming inside files: {old_class_prefix} -> {new_class_prefix}")

for root, dirs, files in os.walk(new_folder):
    for file in files:
        if file.endswith(".script"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="ansi", errors='replace') as f:
                content = f.read()
            content = content.replace(old_class_prefix, new_class_prefix)
            with open(path, "w", encoding="ansi", errors='replace') as f:
                f.write(content)

# Gather mission metadata
print("\nEnter mission metadata:")
display_name = input("Mission name (for menu): ").strip()
briefing_text = input("Briefing text (use \\n for line breaks): ").strip()

objectives = []
while True:
    obj = input("Objective (or press Enter to finish): ").strip()
    if not obj:
        break
    objectives.append(obj)

# Create RSR file
rsr_name = f"Mission{new_class_prefix}.rsr"
rsr_path = os.path.join(new_folder, rsr_name)
with open(rsr_path, "w", encoding="ansi", errors='replace') as f:
    f.write(f"[Mission{new_class_prefix}]\n\n")
    f.write(f"MissionName    =\"{display_name}\"\n")
    f.write(f"BriefingText   =\"{briefing_text}\"\n")
    f.write(f"ObjectivesText =\"{'\\n'.join(objectives)}\"\n\n")
    for i, obj in enumerate(objectives, 1):
        f.write(f"Objective{str(i).zfill(2)}    =\"{obj}\"\n")

print(f"\nRSR file created: {rsr_path}")

# Backup and update MissionsMenu.script
menu_path = os.path.join(tvt_path, "Missions", "MissionsMenu.script")
menu_backup = os.path.join(tvt_path, "Missions", "MissionsMenu.script.bak")

if os.path.exists(menu_path):
    shutil.copy(menu_path, menu_backup)
    print("\nBacked up MissionsMenu.script -> .bak")

    # Ask to add to menu
    add_to_menu = input("Add to MissionsMenu.script now? (Y/N): ").strip().lower()
    if add_to_menu == 'y':
        with open(menu_path, "r", encoding="ansi", errors='replace') as f:
            content = f.read()
        insert_point = content.rfind("];")
        if insert_point != -1:
            entry = f'    ["{display_name}", "C{new_class_prefix}Mission"],\n'
            updated = content[:insert_point] + entry + content[insert_point:]
            with open(menu_path, "w", encoding="ansi", errors='replace') as f:
                f.write(updated)
            print("Mission added to MissionsMenu.script.")
        else:
            print("Error: Could not insert into MissionsMenu.script.")
    else:
        print("Skipped menu insertion.")
else:
    print("Warning: MissionsMenu.script not found.")

print("\n--- All done ---")
