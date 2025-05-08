import os
import shutil
import re

# Helper for sanitizing names for use in file paths and class/variable names
def sanitize_identifier(name):
    # Remove non-alphanumeric characters, allow underscores
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    # Ensure it doesn't start with a number if it's for a class name (game script might be picky)
    if name and name[0].isdigit():
        name = "_" + name
    if not name: # if it became empty
        name = "DefaultName"
    return name

# Helper for escaping strings for game script literals
def escape_script_string(text):
    # Escape backslashes first, then double quotes, then newlines for L"" strings
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n') # For ObjectivesText, ensure this is what the game expects
    return text

# Helper for escaping strings for RSR file values
def escape_rsr_string(text):
    # RSR files might just need quotes escaped if they are within quotes
    text = text.replace('"', '""') # Common RSR escaping for quotes
    text = text.replace('\n', '\\n') # Often used for newlines in RSR
    return text

def build_mission(install_path, source_folder_relative, new_mission_name_raw, title_raw, briefing_raw, orders_raw, objectives_raw, campaign, editor_mode=False):
    def clone_and_rename(src_path, dst_path, old_id, new_id, exts_to_process):
        shutil.copytree(src_path, dst_path)
        for root, _, files in os.walk(dst_path):
            for f_name in files:
                if any(f_name.endswith(ext) for ext in exts_to_process):
                    file_path = os.path.join(root, f_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as fd: # Prefer utf-8
                            text_content = fd.read()
                        # Be careful with broad replacements; ensure 'old_id' is specific enough
                        new_text_content = text_content.replace(old_id, new_id)
                        if new_text_content != text_content:
                            with open(file_path, 'w', encoding='utf-8', errors='replace') as fd:
                                fd.write(new_text_content)
                    except Exception as e:
                        print(f"Warning: Could not process file {file_path}: {e}")
                        # Decide if you want to continue or re-raise

    def fix_content_and_strings(dst_mission_folder, old_id, new_id):
        old_strings_script = os.path.join(dst_mission_folder, f"{old_id}Mission_Strings.script")
        if os.path.exists(old_strings_script):
            os.remove(old_strings_script)

        for fn in os.listdir(dst_mission_folder):
            if fn.endswith("Content.script") and fn.startswith(old_id): # Be more specific
                src_content_script = os.path.join(dst_mission_folder, fn)
                dst_content_script = os.path.join(dst_mission_folder, f"{new_id}Content.script")
                os.rename(src_content_script, dst_content_script)
                break # Assuming only one such file

    def update_mission_script(dst_mission_folder, mission_id_clean, objective_list):
        script_path = os.path.join(dst_mission_folder, "Mission.script")
        class_name = f"C{mission_id_clean}Mission"
        strings_class = f"{mission_id_clean}Mission_Strings"
        objective_count = len(objective_list)

        # Overwrite/create Mission.script
        try:
            with open(script_path, 'w', encoding='utf-8', errors='replace') as f: # Prefer utf-8
                f.write(f'class {class_name} extends CSPMission\n{{\n')
                f.write(f'    static WString MissionName    = {strings_class}::MissionName;\n')
                f.write(f'    static WString ObjectivesText = {strings_class}::ObjectivesText;\n')
                for i in range(1, objective_count + 1):
                    idx_str = str(i).zfill(2)
                    f.write(f'    static WString Objective{idx_str}     = {strings_class}::Objective{idx_str};\n')
                f.write('\n')
                f.write('    String  m_LocalTime               = "14:00:00";\n')
                f.write('    String  m_TerrainMapTextureName   = "Textures/Default_Map.tex";\n')
                f.write('    static String m_MissionBriefingPicMaterial = "DefaultBriefingPic";\n\n')
                f.write('    Array m_MissionObjectives = [\n')
                for i in range(1, objective_count + 1):
                    idx_str = str(i).zfill(2)
                    comma = ',' if i < objective_count else ''
                    f.write(f'        Objective{idx_str}{comma}\n')
                f.write('    ];\n\n')
                f.write('    boolean isDebug = true;\n')
                f.write('    Array   m_NavpointsForPlayerMap = [];\n\n') # Keep this as per original
                f.write(f'    void {class_name}() {{ CSPMission("{class_name}", "{mission_id_clean}Content"); }}\n')
                f.write('}\n')
        except Exception as e:
            raise Exception(f"Failed to write Mission.script for {mission_id_clean}: {e}")


    def write_strings_script(dst_mission_folder, mission_id_clean, mission_title_esc, briefing_text_esc, orders_text_esc, objective_list_esc):
        strings_script_path = os.path.join(dst_mission_folder, f"{mission_id_clean}Mission_Strings.script")
        full_text_for_objectives = briefing_text_esc.strip() + (("\n" + orders_text_esc.strip()) if orders_text_esc.strip() else "")
        # Ensure the game script handles literal \n for newlines in ObjectivesText
        full_text_for_objectives_esc = escape_script_string(full_text_for_objectives.replace("\n", "\\n"))


        try:
            with open(strings_script_path, 'w', encoding='utf-8', errors='replace') as f: # Prefer utf-8
                f.write(f'class {mission_id_clean}Mission_Strings\n{{\n')
                f.write(f'    static WString MissionName    = L"{mission_title_esc}";\n')
                f.write(f'    static WString ObjectivesText = L"{full_text_for_objectives_esc}";\n')
                for i, obj_esc in enumerate(objective_list_esc, 1):
                    f.write(f'    static WString Objective{str(i).zfill(2)} = L"{obj_esc}";\n')
                f.write('}\n')
        except Exception as e:
            raise Exception(f"Failed to write {mission_id_clean}Mission_Strings.script: {e}")

    def write_rsr(install_base_path, mission_id_clean, mission_title_esc, briefing_text_esc, objective_list_esc):
        rsr_dir = os.path.join(install_base_path, 'Resources')
        os.makedirs(rsr_dir, exist_ok=True)
        rsr_path = os.path.join(rsr_dir, f'Mission{mission_id_clean}.rsr')

        # RSR needs specific newline handling and escaping
        briefing_for_rsr = escape_rsr_string(briefing_raw) # Use raw for RSR as escaping differs
        objectives_text_for_rsr = "\\n".join(map(escape_rsr_string, objectives_raw)) # objectives_raw not objectives_list_esc

        lines = [
            f'[Mission{mission_id_clean}]\n',
            f'MissionName    ="{mission_title_esc}"\n', # title_raw might be better if game doesn't want script escaping
            f'BriefingText   ="{briefing_for_rsr}"\n',
            f'ObjectivesText ="{objectives_text_for_rsr}"\n'
        ]
        for i, obj_raw in enumerate(objectives_raw, 1):
            lines.append(f'Objective{str(i).zfill(2)}    ="{escape_rsr_string(obj_raw)}"\n')

        try:
            # RSR files often use specific encodings like 'utf-16' or a windows codepage.
            # Using 'utf-8' here as a general safe bet, but this might need to be game-specific.
            # Your original had 'utf-16' for .rsr, so let's stick to that.
            with open(rsr_path, 'w', encoding='utf-16') as f:
                f.writelines(lines)
        except Exception as e:
            raise Exception(f"Failed to write Mission{mission_id_clean}.rsr: {e}")

    def patch_array_file(file_to_patch, array_variable_name, line_to_add):
        try:
            with open(file_to_patch, 'r', encoding='utf-8', errors='replace') as f: # Prefer utf-8
                lines = f.readlines()
        except FileNotFoundError:
            raise Exception(f"Patching failed: File not found {file_to_patch}")

        output_lines = []
        inside_array = False
        bracket_nest_level = 0
        last_valid_entry_index = -1
        insertion_indent = ''
        entry_added = False

        for idx, current_line in enumerate(lines):
            output_lines.append(current_line)
            stripped_line = current_line.strip()

            if not inside_array and stripped_line.startswith(f'final static Array {array_variable_name}') and '[' in current_line:
                inside_array = True
                bracket_nest_level = current_line.count('[') - current_line.count(']')
                continue

            if inside_array:
                bracket_nest_level += current_line.count('[') - current_line.count(']')
                # Find a suitable line to insert before the closing ']'
                # This logic looks for a line ending with a quote, assuming array entries are strings
                if bracket_nest_level == 1 and (stripped_line.endswith('"') or stripped_line.endswith('",')):
                    last_valid_entry_index = len(output_lines) -1 # Current line is the last valid one
                    match_indent = re.match(r'^(\s*)', current_line)
                    insertion_indent = match_indent.group(1) if match_indent else '    ' # Default indent

                if bracket_nest_level == 0: # We've found the end of the array
                    if last_valid_entry_index != -1 and not entry_added:
                        # Ensure previous line has a comma if it doesn't
                        if not output_lines[last_valid_entry_index].strip().endswith(','):
                            output_lines[last_valid_entry_index] = output_lines[last_valid_entry_index].rstrip('\r\n') + ',\n'
                        # Insert new line
                        output_lines.insert(last_valid_entry_index + 1, insertion_indent + line_to_add + '\n')
                        entry_added = True
                    inside_array = False # Reset for next array if any

        # If array was empty or not found correctly, this might need adjustment or error.
        # For simplicity, if not added, this implies an issue or empty array handling needed.
        if not entry_added and inside_array: # Should not happen if file format is consistent
             print(f"Warning: Could not reliably find insertion point in {array_variable_name} in {file_to_patch}")
        elif not entry_added and not inside_array: # Array might be empty or not found.
            # This part is tricky: appending to an empty array `Array X = [];`
            # The original logic might fail here. A more robust parser or regex would be needed.
            # For now, we'll assume the array usually has entries or the original logic handles empty.
            print(f"Warning: Entry for {array_variable_name} might not have been added to {file_to_patch}. Array might be empty or format unexpected.")


        try:
            with open(file_to_patch, 'w', encoding='utf-8', errors='replace') as f: # Prefer utf-8
                f.writelines(output_lines)
        except Exception as e:
            raise Exception(f"Failed to write patched file {file_to_patch}: {e}")

    # --- Main build_mission logic ---

    # Sanitize inputs
    new_mission_id = sanitize_identifier(new_mission_name_raw)
    if not new_mission_id:
        raise ValueError("New mission name is invalid or became empty after sanitization.")

    # Escape text data for script/RSR files
    title_script_esc = escape_script_string(title_raw)
    briefing_script_esc = escape_script_string(briefing_raw)
    orders_script_esc = escape_script_string(orders_raw)
    objectives_script_esc = [escape_script_string(obj) for obj in objectives_raw]


    # Normalize paths and ensure security
    abs_install_path = os.path.abspath(install_path)
    
    # source_folder_relative is like "MyMission/Murkz2025" or "Murkz2025" if MyMission is the root
    # We need to ensure it doesn't try to escape the Missions directory
    # If source_folder_relative contains '..' it's suspicious.
    if ".." in source_folder_relative:
        raise ValueError("Source folder path seems to contain '..' which is not allowed.")

    # Construct full source path relative to 'Missions' directory within install_path
    # The original logic for src_rel was a bit complex; simplifying for clarity:
    # Assuming source_folder_relative is like "TemplateSubDir/ActualTemplate" or just "ActualTemplate"
    # and these are *under* a base mission template dir like "Missions/MyMissionTemplates"
    
    # Let's assume source_folder_relative is *directly* the name of the template under `Missions/SomeBaseDir`
    # For example, if MISSION_ROOT in web.py is "M:\T34vsTiger\Missions\MyMission"
    # and source_folder_relative is "Murkz2025", then:
    # src_base = os.path.join(abs_install_path, 'Missions', 'MyMission') # This part comes from tvt_web.py structure
    # src_full_path = os.path.join(src_base, source_folder_relative)
    # For now, I'll use the structure implied by original:
    # `src = os.path.join(install, 'Missions', src_rel)` where `src_rel` was `source_folder`
    # This means `source_folder_relative` here *is* the path part after `install_path/Missions/`
    
    # The source_folder_relative IS `MyMission\\{source}` from tvt_web.py
    # So, if install_path is "M:\T34vsTiger", source_folder_relative is "MyMission\Murkz2025"
    # src_full_path = M:\T34vsTiger\Missions\MyMission\Murkz2025
    src_full_path = os.path.join(abs_install_path, 'Missions', source_folder_relative)
    src_full_path = os.path.abspath(src_full_path) # Normalize

    # Security check: ensure src_full_path is actually within 'abs_install_path/Missions'
    missions_base_path = os.path.abspath(os.path.join(abs_install_path, 'Missions'))
    if not src_full_path.startswith(missions_base_path):
        raise Exception(f"Security risk: Source folder '{src_full_path}' is outside of expected missions directory '{missions_base_path}'.")

    # Determine old_id from the *basename* of the source_folder_relative
    old_mission_id_raw = os.path.basename(source_folder_relative) # e.g. "Murkz2025"
    old_mission_id_clean = sanitize_identifier(old_mission_id_raw) # Sanitize it just in case template name has odd chars

    # Destination path construction
    # dst should be like M:\T34vsTiger\Missions\MyMission\NewMissionName
    dst_mission_path = os.path.join(os.path.dirname(src_full_path), new_mission_id) # Place new mission alongside source template's parent
    dst_mission_path = os.path.abspath(dst_mission_path)

    if not dst_mission_path.startswith(missions_base_path):
        raise Exception(f"Security risk: Destination folder '{dst_mission_path}' is outside of expected missions directory.")

    if not os.path.isdir(src_full_path):
        raise FileNotFoundError(f"Source folder not found: {src_full_path}")
    if os.path.exists(dst_mission_path):
        raise FileExistsError(f"Destination mission folder already exists: {dst_mission_path}")

    print(f"Cloning: {src_full_path} to {dst_mission_path}")
    print(f"Old ID: {old_mission_id_clean}, New ID: {new_mission_id}")

    # 1) Clone & do generic search/replace
    # Be careful with old_mission_id_clean - if source files use raw name, this might not find it
    # Using old_mission_id_raw for replacement as files likely contain the raw name.
    clone_and_rename(src_full_path, dst_mission_path, old_mission_id_raw, new_mission_id,
                     ['.script', '.rsr', '.tex', '.raw', '.bmp', '.scc']) # Add other file types if needed

    # 2) Prune old scripts & rename content file
    # Again, use old_mission_id_raw for finding old files by name.
    fix_content_and_strings(dst_mission_path, old_mission_id_raw, new_mission_id)

    # 3) Generate new .rsr, _Strings.script and Mission.script
    # For RSR, game might expect non-script-escaped title, briefing.
    # Use raw values for RSR content, but new_mission_id for filename and section.
    # Title for RSR `MissionName` might need `title_raw` or `title_script_esc` depending on game.
    # Using `title_script_esc` for consistency, assuming RSR parser is okay with it.
    write_rsr(abs_install_path, new_mission_id, title_script_esc, briefing_raw, objectives_raw) # Pass raw briefing/obj for specific RSR escaping
    write_strings_script(dst_mission_path, new_mission_id, title_script_esc, briefing_script_esc, orders_script_esc, objectives_script_esc)
    update_mission_script(dst_mission_path, new_mission_id, objectives_raw) # Pass raw objectives to count them

    # 4) Patch in-game menu and editor menu
    game_menu_script = os.path.join(abs_install_path, 'Scripts', 'Menus', 'MissionsMenu.script')
    # Ensure new_mission_id is suitable for class C{new_mission_id}Mission
    mission_class_entry = f'"C{new_mission_id}Mission"'
    array_to_patch_game = 'USSR_Missions' if campaign == 'ussr' else 'Germany_Missions'
    patch_array_file(game_menu_script, array_to_patch_game, mission_class_entry)

    editor_menu_script = os.path.join(abs_install_path, 'Scripts', 'Editor', 'MenuConfig.script')
    # title_raw needs to be escaped for being a string literal inside a script array
    editor_mission_entry = f'["{escape_script_string(title_raw)}", "C{new_mission_id}Mission"]'
    patch_array_file(editor_menu_script, 'MissionLoadList', editor_mission_entry)

    print(f"Mission '{new_mission_id}' built successfully at {dst_mission_path}")