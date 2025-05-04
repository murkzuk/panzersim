import os, shutil, re

def build_mission(install_path, source_folder, new_name, title, briefing, orders, objectives, campaign, editor_mode=False):
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

    # New helper: remove stray files and rename your content script
    def fix_content_and_strings(dst_folder, old, new):
        # 1) Remove the old strings script
        old_strings = os.path.join(dst_folder, f"{old}Mission_Strings.script")
        if os.path.exists(old_strings):
            os.remove(old_strings)

        # 2) Find any *Content.script in the folder and rename it to <new>Content.script
        for fn in os.listdir(dst_folder):
            if fn.endswith("Content.script"):
                src = os.path.join(dst_folder, fn)
                dst = os.path.join(dst_folder, f"{new}Content.script")
                os.rename(src, dst)
                break

    def update_mission_script(dst_folder, new_name, objective_count):
        script_path = os.path.join(dst_folder, "Mission.script")
        class_name = f"C{new_name}Mission"
        strings_class = f"{new_name}Mission_Strings"
        if os.path.exists(script_path):
            with open(script_path, 'w', encoding='ansi', errors='ignore') as f:
                f.write(f'class {class_name} extends CSPMission\n{{\n')
                f.write(f'    static WString MissionName    = {strings_class}::MissionName;\n')
                f.write(f'    static WString ObjectivesText = {strings_class}::ObjectivesText;\n')
                # Write individual ObjectiveXX fields
                for i in range(1, objective_count + 1):
                    idx = str(i).zfill(2)
                    f.write(f'    static WString Objective{idx}     = {strings_class}::Objective{idx};\n')
                f.write('\n')
                f.write('    String  m_LocalTime               = "14:00:00";\n')
                f.write('    String  m_TerrainMapTextureName   = "Textures/Default_Map.tex";\n')
                f.write('    static String m_MissionBriefingPicMaterial = "DefaultBriefingPic";\n\n')
                # Objectives array, no trailing comma on last entry
                f.write('    Array m_MissionObjectives = [\n')
                for i in range(1, objective_count + 1):
                    idx = str(i).zfill(2)
                    comma = ',' if i < objective_count else ''
                    f.write(f'        Objective{idx}{comma}\n')
                f.write('    ];\n\n')
                f.write('    boolean isDebug = true;\n')
                f.write('    Array   m_NavpointsForPlayerMap = [];\n\n')
                f.write(f'    void {class_name}() {{ CSPMission("{class_name}", "{new_name}Content"); }}\n')
                f.write('}\n')

    def write_strings_script(dst_folder, new_name, title, briefing, orders, objectives):
        full_text = briefing.strip() + ("\n" + orders.strip() if orders.strip() else "")
        path = os.path.join(dst_folder, f"{new_name}Mission_Strings.script")
        with open(path, 'w', encoding='ansi', errors='ignore') as f:
            f.write(f'class {new_name}Mission_Strings\n{{\n')
            f.write(f'    static WString MissionName    = L"{title}";\n')
            f.write(f'    static WString ObjectivesText = L"{full_text.replace(chr(10), r"\\n")}";\n')
            for i, obj in enumerate(objectives, 1):
                f.write(f'    static WString Objective{str(i).zfill(2)} = L"{obj}";\n')
            f.write('}\n')

    def write_rsr(install, new, title, brief, objs):
        rsr_dir = os.path.join(install, 'Resources')
        os.makedirs(rsr_dir, exist_ok=True)
        rsr_path = os.path.join(rsr_dir, f'Mission{new}.rsr')
        lines = [
            f'[Mission{new}]\n',
            f'MissionName    ="{title}"\n',
            f'BriefingText   ="{brief}"\n',
            f'ObjectivesText ="{"\\n".join(objs)}"\n'
        ]
        for i, obj in enumerate(objs, 1):
            lines.append(f'Objective{str(i).zfill(2)}    ="{obj}"\n')
        with open(rsr_path, 'w', encoding='utf-16') as f:
            f.writelines(lines)

    def patch_array(file_path, array_name, entry_line):
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

    install = install_path.rstrip('/\\')
    src_rel = source_folder.lstrip('/\\')
    if src_rel.lower().startswith('missions' + os.sep.lower()):
        src_rel = os.sep.join(src_rel.split(os.sep)[1:])
    src = os.path.join(install, 'Missions', src_rel)
    dst = os.path.join(install, 'Missions', os.path.dirname(src_rel), new_name)
    old = os.path.basename(src_rel)
    new = new_name

    if not os.path.isdir(src):
        raise Exception(f"Source folder not found: {src}")
    if os.path.exists(dst):
        raise Exception(f"Destination already exists: {dst}")

    # 1) Clone & do your generic search/replace
    clone_and_rename(src, dst, old, new, ['.script', '.rsr', '.tex', '.raw', '.bmp', '.scc'])

    # 2) Prune the old leftover scripts & rename your content file
    fix_content_and_strings(dst, old, new)

    # 3) Generate the new .rsr, _Strings.script and Mission.script properly
    write_rsr(install, new, title, briefing, objectives)
    write_strings_script(dst, new, title, briefing, orders, objectives)
    update_mission_script(dst, new, len(objectives))

    # 4) Patch both the in-game menu and the editor menu
    game_menu   = os.path.join(install, 'Scripts', 'Menus', 'MissionsMenu.script')
    arr         = 'USSR_Missions' if campaign == 'ussr' else 'Germany_Missions'
    patch_array(game_menu, arr, f'"C{new}Mission"')

    editor_menu = os.path.join(install, 'Scripts', 'Editor', 'MenuConfig.script')
    entry2      = f'[\"{title}\", \"C{new}Mission\"]'
    patch_array(editor_menu, 'MissionLoadList', entry2)
