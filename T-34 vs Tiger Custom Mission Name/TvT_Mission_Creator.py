#!/usr/bin/env python3
"""
T-34 vs Tiger Mission Builder

Automates:
1. Copy an existing mission folder (path can be absolute or relative to install/Missions).
2. Rename class prefixes in .script files (Mission, Content, etc.).
3. Create a new .rsr file with correct [Mission...] section.
4. Backup and patch MissionsMenu.script.
5. Backup and patch MenuConfig.script.

Usage examples:
# Using relative source under install/Missions:
python TvT_Mission_Creator.py \
  --install "M:/T34vsTiger" \
  --source "MyMission/jeff_first_skirmish" \
  --new Testing6 \
  --title "Jeff test 6" \
  --brief "Mission briefing here" \
  --obj "Advance to crossroad" --obj "Destroy AT guns"

# Using absolute source path:
python TvT_Mission_Creator.py \
  --install "M:/T34vsTiger" \
  --source "M:/T34vsTiger/Missions/MyMission/jeff_first_skirmish" \
  --new Testing6 \
  --title "Jeff test 6" \
  --brief "Mission briefing here" \
  --obj "Advance to crossroad"
"""
import os
import shutil
import argparse
import sys
import re

def normalize_path(path: str) -> str:
    return os.path.normpath(path.strip('"').strip("'"))

def resolve_source(install: str, src_arg: str) -> str:
    src_norm = normalize_path(src_arg)
    # if absolute or exists, use directly
    if os.path.isdir(src_norm):
        return src_norm
    # else try under install/Missions
    candidate = os.path.join(install, 'Missions', src_norm)
    if os.path.isdir(candidate):
        return candidate
    raise FileNotFoundError(f"Source folder not found (tried '{src_norm}' and '{candidate}').")

def copy_mission(src: str, dst: str) -> None:
    if os.path.exists(dst):
        raise FileExistsError(f"Target folder already exists: {dst}")
    shutil.copytree(src, dst)

def rename_scripts(mission_dir: str, old_prefix: str, new_prefix: str) -> int:
    updated = 0
    pat = re.compile(rf"\b{re.escape(old_prefix)}(Mission|Content)\b")
    for root, _, files in os.walk(mission_dir):
        for fname in files:
            if fname.endswith('.script'):
                path = os.path.join(root, fname)
                txt = open(path, 'r', encoding='utf-8', errors='ignore').read()
                new_txt = pat.sub(lambda m: m.group(0).replace(old_prefix, new_prefix), txt)
                if new_txt != txt:
                    open(path, 'w', encoding='utf-8', errors='ignore').write(new_txt)
                    updated += 1
    return updated

def create_rsr(mission_dir: str, prefix: str, title: str, briefing: str, objectives: list[str]) -> str:
    fn = f"Mission{prefix}.rsr"
    path = os.path.join(mission_dir, fn)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"[Mission{prefix}]\n")
        f.write(f"MissionName    = \"{title}\"\n")
        f.write(f"BriefingText   = \"{briefing}\"\n")
        f.write(f"ObjectivesText = \"{'\\n'.join(objectives)}\"\n")
        for idx, obj in enumerate(objectives, 1):
            f.write(f"Objective{idx:02d}    = \"{obj}\"\n")
    return path

def backup_and_patch(path: str, backup_ext: str, entry: str, marker: str = '];') -> bool:
    if not os.path.isfile(path): return False
    shutil.copy(path, path + backup_ext)
    txt = open(path, 'r', encoding='utf-8', errors='ignore').read()
    pos = txt.rfind(marker)
    if pos == -1: return False
    patched = txt[:pos] + entry + '\n' + txt[pos:]
    open(path, 'w', encoding='utf-8', errors='ignore').write(patched)
    return True

def main():
    p = argparse.ArgumentParser(description='T-34 vs Tiger Mission Builder')
    p.add_argument('--install', required=True)
    p.add_argument('--source',  required=True, help='Absolute path or relative under install/Missions')
    p.add_argument('--new',     required=True, help='New mission folder name')
    p.add_argument('--title',   required=True)
    p.add_argument('--brief',   required=True)
    p.add_argument('--obj',     action='append', default=[] )
    args = p.parse_args()

    install = normalize_path(args.install)
    try:
        src = resolve_source(install, args.source)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    dst = os.path.join(os.path.dirname(src), args.new)
    oldp = os.path.basename(src)
    newp = args.new

    try:
        copy_mission(src, dst)
        print(f"Copied '{src}' → '{dst}'")
    except Exception as e:
        print(f"Copy error: {e}", file=sys.stderr)
        sys.exit(1)

    cnt = rename_scripts(dst, oldp, newp)
    print(f"Renamed {cnt} .script files")

    rsr_path = create_rsr(dst, newp, args.title, args.brief, args.obj)
    print(f"Created RSR: {rsr_path}")

    entry = f'    ["{args.title}", "C{newp}Mission"],'    
    mm = os.path.join(install, 'Scripts', 'Menus', 'MissionsMenu.script')
    if backup_and_patch(mm, '.bak', entry):
        print("Patched MissionsMenu.script")
    else:
        print("Skipped MissionsMenu.script (not found or no marker)")

    ec = os.path.join(install, 'Scripts', 'Editor', 'MenuConfig.script')
    if backup_and_patch(ec, '.bak', entry):
        print("Patched MenuConfig.script")
    else:
        print("Skipped MenuConfig.script (not found or no marker)")

if __name__ == '__main__':
    main()
