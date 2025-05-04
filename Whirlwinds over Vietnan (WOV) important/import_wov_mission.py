import os, shutil, re, argparse

def discover_old_id(mission_dir):
    for root, _, files in os.walk(mission_dir):
        for file in files:
            if file.endswith('.rsr'):
                content = open(os.path.join(root, file), encoding='utf-16', errors='ignore').read()
                m = re.search(r'\[Mission([^\]]+)\]', content)
                if m:
                    return m.group(1)
    return None

def replace_in_file(patterns, path):
    text = open(path, 'r', encoding='utf-16', errors='ignore').read()
    for old, new in patterns:
        text = text.replace(old, new)
    open(path, 'w', encoding='utf-16').write(text)

def patch_menu(file_path, new_name):
    lines = []
    in_block = False
    for line in open(file_path, 'r', encoding='utf-8', errors='ignore'):
        stripped = line.strip()
        if stripped.startswith("USSRMissions") or stripped.startswith("GermanyMissions"):
            in_block = True
            lines.append(line)
            continue
        if in_block and stripped.startswith("}"):
            lines.append(f'    "{new_name}",\n')
            lines.append(line)
            in_block = False
            continue
        lines.append(line)
    open(file_path, 'w', encoding='utf-8').writelines(lines)

def main():
    parser = argparse.ArgumentParser(description="Import WoV mission into TvT")
    parser.add_argument("source", help="Path to source WoV mission folder")
    parser.add_argument("install", help="Path to TvT root (contains Missions folder and menu scripts)")
    parser.add_argument("--name", default="WoVtest", help="New mission name")
    args = parser.parse_args()

    src = args.source
    root = args.install
    new_name = args.name

    dest = os.path.join(root, 'Missions', new_name)
    if os.path.exists(dest):
        print(f"Destination {dest} already exists. Aborting.")
        return

    # Copy the mission folder
    shutil.copytree(src, dest)
    print(f"Copied mission folder to {dest}")

    # Discover the old mission ID
    old_id = discover_old_id(dest)
    if not old_id:
        print("Could not discover old mission ID in RSR files. Aborting.")
        return

    # Rename and replace inside mission files
    for dirpath, _, filenames in os.walk(dest):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if filename.endswith('.rsr'):
                new_filename = filename.replace(old_id, new_name)
                os.rename(path, os.path.join(dirpath, new_filename))
                path = os.path.join(dirpath, new_filename)
                replace_in_file([(f"[Mission{old_id}]", f"[Mission{new_name}]")], path)
            elif filename.endswith('.script'):
                replace_in_file([
                    (f"Mission{old_id}", f"Mission{new_name}"),
                    (f"MissionStrings_{old_id}", f"MissionStrings_{new_name}")
                ], path)

    # Patch the menu scripts
    patch_menu(os.path.join(root, 'MissionsMenu.script'), new_name)
    patch_menu(os.path.join(root, 'MenuConfig.script'), new_name)
    print("Patched MissionsMenu.script and MenuConfig.script")

if __name__ == "__main__":
    main()
