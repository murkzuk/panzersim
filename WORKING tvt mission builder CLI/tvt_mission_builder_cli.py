import os
import shutil
import argparse
import sys
import re

def clone_and_rename(src, dst, old, new, exts):
    shutil.copytree(src, dst)
    for root, _, files in os.walk(dst):
        for f in files:
            if any(f.endswith(ext) for ext in exts):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='ansi', errors='ignore') as fd:
                    text = fd.read()
                new_text = text.replace(old, new)
                if new_text != text:
                    with open(path, 'w', encoding='ansi', errors='ignore') as fd:
                        fd.write(new_text)
    print(f"Renamed occurrences of '{old}' → '{new}'")

def write_rsr(install, new, title, brief, objs):
    rsr_dir = os.path.join(install, 'Resources')
    os.makedirs(rsr_dir, exist_ok=True)
    rsr_path = os.path.join(rsr_dir, f'Mission{new}.rsr')
    lines = [f'[Mission{new}]\n',
             f'MissionName    ="{title}"\n',
             f'BriefingText   ="{brief}"\n',
             f'ObjectivesText ="{'\\n'.join(objs)}"\n']
    for i, obj in enumerate(objs, 1):
        lines.append(f'Objective{str(i).zfill(2)}    ="{obj}"\n')
    with open(rsr_path, 'w', encoding='utf-16') as f:
        f.writelines(lines)
    print(f"Created RSR: {rsr_path}")
    return rsr_path

def backup(file_path):
    bak = file_path + '.bak'
    if os.path.exists(file_path):
        shutil.copy(file_path, bak)
        print(f"Backed up {file_path} → {bak}")
    else:
        print(f"Warning: {file_path} not found, skipping backup.")

def patch_array(file_path, array_name, entry_line):
    backup(file_path)
    with open(file_path, 'r', encoding='ansi', errors='ignore') as f:
        lines = f.readlines()

    output = []
    inside = False
    bracket_level = 0
    last_insert_index = -1
    insert_indent = ''

    for idx, line in enumerate(lines):
        stripped = line.strip()
        output.append(line)

        if not inside and stripped.startswith(f'final static Array {array_name}') and '[' in line:
            inside = True
            bracket_level = 1
            continue

        if inside:
            bracket_level += line.count('[') - line.count(']')

            if bracket_level == 1 and stripped.endswith('"'):
                last_insert_index = idx
                match = re.match(r'^(\s*)', line)
                insert_indent = match.group(1) if match else ''

            if bracket_level == 0:
                if last_insert_index != -1:
                    if not output[last_insert_index].strip().endswith(','):
                        output[last_insert_index] = output[last_insert_index].rstrip() + ',\n'
                    output.insert(last_insert_index + 1, insert_indent + entry_line + '\n')
                inside = False

    with open(file_path, 'w', encoding='ansi', errors='ignore') as f:
        f.writelines(output)
    print(f"Patched {array_name} in {file_path}")

def main():
    p = argparse.ArgumentParser(description="Clone a TVT mission and register it in menus")
    p.add_argument('-i','--install', required=True, help='Root path of T34vsTiger install')
    p.add_argument('-s','--source', required=True, help='Relative mission folder under Missions/')
    p.add_argument('-n','--new', required=True, help='New mission folder name (no spaces)')
    p.add_argument('-e','--ext', nargs='+', default=['.script'], help='File extensions to rename')
    p.add_argument('--title', required=True, help='Display mission name')
    p.add_argument('--brief', required=True, help='Briefing text (\\n for line breaks)')
    p.add_argument('--obj', action='append', default=[], help='Objective text (can repeat)')
    p.add_argument('--campaign', choices=['ussr','germany'], help='Which campaign list to patch')
    p.add_argument('-y','--yes', action='store_true', help='Skip confirmations')
    args = p.parse_args()

    if not args.campaign:
        while True:
            choice = input("Select campaign ([U]SSR / [G]ermany): ").strip().upper()
            if choice == 'U':
                args.campaign = 'ussr'
                break
            elif choice == 'G':
                args.campaign = 'germany'
                break
            else:
                print("Invalid choice. Please enter 'U' or 'G'.")

    install = args.install.rstrip('\\/')
    src_rel = args.source.lstrip('/\\')
    if src_rel.lower().startswith('missions' + os.sep.lower()):
        src_rel = os.sep.join(src_rel.split(os.sep)[1:])
    src = os.path.join(install, 'Missions', src_rel)
    dst = os.path.join(install, 'Missions', os.path.dirname(src_rel), args.new)
    old = os.path.basename(src_rel)
    new = args.new

    if not os.path.isdir(src):
        print(f"Error: Source folder not found: {src}")
        sys.exit(1)
    if os.path.exists(dst):
        print(f"Error: Destination already exists: {dst}")
        sys.exit(1)

    print(f"Cloning {src} → {dst}")
    clone_and_rename(src, dst, old, new, args.ext)

    rsr = write_rsr(install, new, args.title, args.brief, args.obj)

    game_menu = os.path.join(install, 'Scripts', 'Menus', 'MissionsMenu.script')
    arr = 'USSR_Missions' if args.campaign=='ussr' else 'Germany_Missions'
    entry = f'"C{new}Mission"'
    patch_array(game_menu, arr, entry)

    editor_menu = os.path.join(install, 'Scripts', 'Editor', 'MenuConfig.script')
    entry2 = f'["{args.title.replace("\"", "\\\"")}", "C{new}Mission"]'
    patch_array(editor_menu, 'MissionLoadList', entry2)

    print("\nAll done! Your new mission is ready.")

if __name__=='__main__':
    main()
