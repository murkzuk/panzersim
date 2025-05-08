import os
import shutil
import re

# Helper for sanitizing names for use in file paths and class/variable names
def sanitize_identifier(name):
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if name and name[0].isdigit():
        name = "_" + name
    if not name:
        name = "DefaultName"
    return name

# Helper for escaping strings for game script literals (L"...")
def escape_script_string(text):
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n') # For WString newlines
    return text

# Helper for escaping strings for RSR file values ("...")
def escape_rsr_string(text):
    text = text.replace('"', '""')
    text = text.replace('\n', '\\n') # RSR often uses literal \n
    return text

# Helper to get values from the template's Mission.script
def get_value_from_template_script(template_script_path, variable_name):
    """
    Extracts a string variable's value from a Mission.script like file.
    Assumes format like: static String m_VarName = "value";
    """
    try:
        # Use 'cp1252' as it's often the "ANSI" for Western European Windows games for .script files
        with open(template_script_path, 'r', encoding='cp1252', errors='replace') as f:
            for line in f:
                stripped_line = line.strip()
                # Looking for lines like: String m_VarName = "some_value";
                # Or: static WString VarName = L"some_value";
                if variable_name in stripped_line and "=" in stripped_line:
                    try:
                        # Split at '=' and take the part after it
                        value_part = stripped_line.split('=', 1)[1].strip()
                        # Remove trailing semicolon
                        value_part = value_part.rstrip(';')
                        # Remove surrounding quotes (single or double, or L")
                        if value_part.startswith('L"') and value_part.endswith('"'):
                            value = value_part[2:-1] # Strip L" and "
                        elif value_part.startswith('"') and value_part.endswith('"'):
                            value = value_part[1:-1] # Strip " and "
                        else:
                            value = value_part # No quotes or unknown format, take as is
                        
                        # Unescape common script escapes if needed for use,
                        # but for direct re-insertion, this might not be necessary.
                        # For now, return as found in file (potentially still escaped).
                        return value
                    except IndexError:
                        continue # Malformed line or unexpected structure
            return None # Variable not found
    except FileNotFoundError:
        print(f"Warning: Template script {template_script_path} not found for reading variable {variable_name}.")
        return None
    except Exception as e:
        print(f"Warning: Error reading {variable_name} from {template_script_path}: {e}")
        return None

def build_mission(install_path, source_folder_relative, new_mission_name_raw, title_raw, briefing_raw, orders_raw, objectives_raw, campaign, editor_mode=False):
    
    # --- SCRIPT FILE ENCODING (IMPORTANT!) ---
    # TvsT .script files often use a Windows codepage, 'cp1252' (Western European) is common for "ANSI"
    # If this causes issues with special characters for other languages, 'utf-8' might be an alternative,
    # but the game engine might not support it for scripts.
    SCRIPT_ENCODING = 'cp1252'
    SCRIPT_ERROR_HANDLING = 'replace' # 'ignore' can hide problems

    def clone_and_rename(src_path, dst_path, old_id_for_replace, new_id_for_replace, exts_to_process):
        shutil.copytree(src_path, dst_path)
        for root, _, files in os.walk(dst_path):
            for f_name in files:
                if any(f_name.endswith(ext) for ext in exts_to_process):
                    file_path = os.path.join(root, f_name)
                    
                    current_read_encoding = 'utf-8' # Default for non-script binary-like text files
                    current_write_encoding = 'utf-8'

                    if f_name.endswith('.script'):
                        current_read_encoding = SCRIPT_ENCODING
                        current_write_encoding = SCRIPT_ENCODING
                    # Add other specific encodings if known (e.g., .raw, .scc if they are text)

                    try:
                        with open(file_path, 'r', encoding=current_read_encoding, errors=SCRIPT_ERROR_HANDLING) as fd:
                            text_content = fd.read()
                        
                        # Perform replacement: be careful with simple string replace.
                        # It's better to replace specific known identifiers if possible.
                        # For now, using the broader approach based on old_id_for_replace.
                        new_text_content = text_content.replace(old_id_for_replace, new_id_for_replace)
                        
                        if new_text_content != text_content:
                            with open(file_path, 'w', encoding=current_write_encoding, errors=SCRIPT_ERROR_HANDLING) as fd:
                                fd.write(new_text_content)
                    except UnicodeDecodeError as ude:
                        print(f"Warning: UnicodeDecodeError for {file_path} with encoding {current_read_encoding}. File may be binary or wrong encoding. Skipping replacement. Error: {ude}")
                    except Exception as e:
                        print(f"Warning: Could not process file {file_path} for replacement: {e}")

    def fix_content_and_strings(dst_mission_folder, old_id_raw_basename, new_id_clean):
        # Remove the old strings script (e.g., OldMissionNameMission_Strings.script)
        old_strings_script_path = os.path.join(dst_mission_folder, f"{old_id_raw_basename}Mission_Strings.script")
        if os.path.exists(old_strings_script_path):
            try:
                os.remove(old_strings_script_path)
            except Exception as e:
                print(f"Warning: Could not remove old strings script {old_strings_script_path}: {e}")

        # Find any *Content.script that starts with the old mission name and rename it
        # This assumes the Content script is named like "OldMissionNameContent.script"
        found_content_script = False
        for fn in os.listdir(dst_mission_folder):
            # Be more specific: starts with old name, ends with Content.script
            if fn.lower().startswith(old_id_raw_basename.lower()) and fn.lower().endswith("content.script"):
                src_content_script = os.path.join(dst_mission_folder, fn)
                dst_content_script = os.path.join(dst_mission_folder, f"{new_id_clean}Content.script")
                try:
                    os.rename(src_content_script, dst_content_script)
                    found_content_script = True
                    break 
                except Exception as e:
                    print(f"Warning: Could not rename content script from {src_content_script} to {dst_content_script}: {e}")
        if not found_content_script:
            print(f"Warning: No content script starting with '{old_id_raw_basename}' and ending with 'Content.script' found in {dst_mission_folder} to rename.")


    def update_mission_script(dst_mission_folder, mission_id_clean, objective_list, template_mission_script_path_full):
        script_path = os.path.join(dst_mission_folder, "Mission.script")
        class_name = f"C{mission_id_clean}Mission"
        strings_class = f"{mission_id_clean}Mission_Strings"
        objective_count = len(objective_list)

        terrain_map_tex = get_value_from_template_script(template_mission_script_path_full, "m_TerrainMapTextureName") or "Textures/Default_Map.tex"
        briefing_pic_mat = get_value_from_template_script(template_mission_script_path_full, "m_MissionBriefingPicMaterial") or "DefaultBriefingPic"
        local_time_str = get_value_from_template_script(template_mission_script_path_full, "m_LocalTime") or "14:00:00"
        # is_debug_str = get_value_from_template_script(template_mission_script_path_full, "isDebug") or "true" # Example if isDebug was a string "true"/"false"

        try:
            with open(script_path, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                f.write(f'class {class_name} extends CSPMission\n{{\n')
                f.write(f'    static WString MissionName    = {strings_class}::MissionName;\n')
                f.write(f'    static WString ObjectivesText = {strings_class}::ObjectivesText;\n')
                for i in range(1, objective_count + 1):
                    idx_str = str(i).zfill(2)
                    f.write(f'    static WString Objective{idx_str}     = {strings_class}::Objective{idx_str};\n')
                f.write('\n')
                f.write(f'    String  m_LocalTime               = "{local_time_str}";\n')
                f.write(f'    String  m_TerrainMapTextureName   = "{terrain_map_tex}";\n')
                f.write(f'    static String m_MissionBriefingPicMaterial = "{briefing_pic_mat}";\n\n')
                f.write('    Array m_MissionObjectives = [\n')
                for i in range(1, objective_count + 1):
                    idx_str = str(i).zfill(2)
                    comma = ',' if i < objective_count else ''
                    f.write(f'        Objective{idx_str}{comma}\n')
                f.write('    ];\n\n')
                f.write(f'    boolean isDebug = true;\n') # Keep true, or parse from template if needed
                f.write('    Array   m_NavpointsForPlayerMap = [];\n\n')
                f.write(f'    void {class_name}() {{ CSPMission("{class_name}", "{mission_id_clean}Content"); }}\n')
                f.write('}\n')
        except Exception as e:
            raise Exception(f"Failed to write Mission.script for {mission_id_clean}: {e}")

    def write_strings_script(dst_mission_folder, mission_id_clean, mission_title_esc, briefing_text_esc, orders_text_esc, objective_list_esc):
        strings_script_path = os.path.join(dst_mission_folder, f"{mission_id_clean}Mission_Strings.script")
        # Combine briefing and orders for the main ObjectivesText, game script typically expects \n for newlines here.
        # The escape_script_string already handles \n -> \\n if needed for literal WString.
        full_text_for_objectives = briefing_raw.strip() + (("\n" + orders_raw.strip()) if orders_raw.strip() else "")
        full_text_for_objectives_esc = escape_script_string(full_text_for_objectives)

        try:
            with open(strings_script_path, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                f.write(f'class {mission_id_clean}Mission_Strings\n{{\n')
                f.write(f'    static WString MissionName    = L"{mission_title_esc}";\n')
                f.write(f'    static WString ObjectivesText = L"{full_text_for_objectives_esc}";\n')
                for i, obj_esc in enumerate(objective_list_esc, 1):
                    f.write(f'    static WString Objective{str(i).zfill(2)} = L"{obj_esc}";\n')
                f.write('}\n')
        except Exception as e:
            raise Exception(f"Failed to write {mission_id_clean}Mission_Strings.script: {e}")

    def write_rsr(install_base_path, mission_id_clean, mission_title_raw, briefing_text_raw, objective_list_raw):
        # RSR files often use specific encodings like 'utf-16'.
        RSR_ENCODING = 'utf-16'
        rsr_dir = os.path.join(install_base_path, 'Resources')
        os.makedirs(rsr_dir, exist_ok=True)
        rsr_path = os.path.join(rsr_dir, f'Mission{mission_id_clean}.rsr')

        # For RSR, escape differently. Often "" for quotes and literal \n.
        title_rsr_esc = escape_rsr_string(mission_title_raw)
        briefing_rsr_esc = escape_rsr_string(briefing_text_raw)
        objectives_text_for_rsr = "\\n".join(map(escape_rsr_string, objective_list_raw))

        lines = [
            f'[Mission{mission_id_clean}]\n',
            f'MissionName    ="{title_rsr_esc}"\n',
            f'BriefingText   ="{briefing_rsr_esc}"\n',
            f'ObjectivesText ="{objectives_text_for_rsr}"\n'
        ]
        for i, obj_raw in enumerate(objective_list_raw, 1):
            lines.append(f'Objective{str(i).zfill(2)}    ="{escape_rsr_string(obj_raw)}"\n')

        try:
            with open(rsr_path, 'w', encoding=RSR_ENCODING) as f:
                f.writelines(lines)
        except Exception as e:
            raise Exception(f"Failed to write Mission{mission_id_clean}.rsr: {e}")

    def patch_array_file(file_to_patch, array_variable_name, line_to_add):
        try:
            with open(file_to_patch, 'r', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise Exception(f"Patching failed: Menu script file not found {file_to_patch}")

        output_lines = []
        inside_array = False
        bracket_nest_level = 0
        last_valid_entry_index = -1
        insertion_indent = ''
        entry_added = False

        for current_line in lines:
            output_lines.append(current_line) # Add line first
            stripped_line = current_line.strip()

            if not inside_array and stripped_line.startswith(f'final static Array {array_variable_name}') and '[' in current_line:
                inside_array = True
                bracket_nest_level = current_line.count('[') - current_line.count(']')
                # If array is empty `Array X = [];` then no last_valid_entry_index will be set by below logic
                # The insertion logic assumes at least one entry or specific formatting.
                if bracket_nest_level == 0 and stripped_line.endswith('[]'): # Empty array `X = []`
                    # Insert directly before the closing ']'
                    last_char_idx = output_lines[-1].rfind(']')
                    if last_char_idx != -1:
                        indent_match = re.match(r'^(\s*)', output_lines[-1])
                        insertion_indent = (indent_match.group(1) if indent_match else "    ") + "    " # Indent further
                        output_lines[-1] = output_lines[-1][:last_char_idx] + "\n" + insertion_indent + line_to_add + "\n" + output_lines[-1][last_char_idx:]
                        entry_added = True
                    inside_array = False # Exit, array was empty.
                continue

            if inside_array:
                bracket_nest_level += current_line.count('[') - current_line.count(']')
                # Consider lines ending with a quote (string entries) or a comma after quote
                if bracket_nest_level == 1 and (stripped_line.endswith('"') or stripped_line.endswith('",')):
                    last_valid_entry_index = len(output_lines) -1 
                    match_indent = re.match(r'^(\s*)', current_line)
                    insertion_indent = match_indent.group(1) if match_indent else '    '

                if bracket_nest_level == 0: # End of array
                    if last_valid_entry_index != -1 and not entry_added:
                        # Ensure previous line has a comma if it's an entry
                        if not output_lines[last_valid_entry_index].strip().endswith(','):
                            output_lines[last_valid_entry_index] = output_lines[last_valid_entry_index].rstrip('\r\n') + ',\n'
                        output_lines.insert(last_valid_entry_index + 1, insertion_indent + line_to_add + '\n')
                        entry_added = True
                    inside_array = False
        
        if not entry_added: # If array was not found or some other issue
            print(f"Warning: Could not reliably find insertion point or add entry to '{array_variable_name}' in {file_to_patch}. Array might be empty or format unexpected, or entry already exists (no check for duplicates).")

        try:
            with open(file_to_patch, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                f.writelines(output_lines)
        except Exception as e:
            raise Exception(f"Failed to write patched menu script file {file_to_patch}: {e}")

    # --- Main build_mission logic ---
    new_mission_id = sanitize_identifier(new_mission_name_raw)
    if not new_mission_id:
        raise ValueError("New mission name is invalid or became empty after sanitization.")

    title_script_esc = escape_script_string(title_raw)
    briefing_script_esc = escape_script_string(briefing_raw) # Used by write_strings_script
    orders_script_esc = escape_script_string(orders_raw)     # Used by write_strings_script
    objectives_script_esc = [escape_script_string(obj) for obj in objectives_raw]

    abs_install_path = os.path.abspath(install_path)
    if ".." in source_folder_relative:
        raise ValueError("Source folder path appears to contain '..' which is not allowed.")

    src_full_path = os.path.join(abs_install_path, 'Missions', source_folder_relative)
    src_full_path = os.path.abspath(src_full_path)

    missions_base_path = os.path.abspath(os.path.join(abs_install_path, 'Missions'))
    if not src_full_path.startswith(missions_base_path):
        raise Exception(f"Security risk: Source folder '{src_full_path}' is outside of expected missions directory '{missions_base_path}'.")

    old_mission_id_raw_basename = os.path.basename(src_full_path) # Get basename of the source template folder itself

    # Destination path: new mission folder will be sibling to source's parent if source is deeply nested,
    # or directly under Missions if source_folder_relative was like "MyMission/Template"
    # Corrected logic: new mission folder should be within the same directory level as the template typically
    # E.g. if template is Missions/MyMission/Template1, new is Missions/MyMission/NewMission
    # If template is Missions/Campaign1/MissionA, new is Missions/Campaign1/NewMission
    dst_mission_path_base = os.path.dirname(src_full_path) # Parent of the template folder
    dst_mission_path = os.path.join(dst_mission_path_base, new_mission_id)
    dst_mission_path = os.path.abspath(dst_mission_path)

    if not dst_mission_path.startswith(missions_base_path):
        raise Exception(f"Security risk: Destination folder '{dst_mission_path}' would be outside of missions directory.")

    if not os.path.isdir(src_full_path):
        raise FileNotFoundError(f"Source folder not found: {src_full_path}")
    if os.path.exists(dst_mission_path):
        raise FileExistsError(f"Destination mission folder already exists: {dst_mission_path}")

    print(f"Cloning: {src_full_path} to {dst_mission_path}")
    print(f"Old ID (basename for replace): {old_mission_id_raw_basename}, New ID (folder/class): {new_mission_id}")

    # 1) Clone & do generic search/replace
    # Extensions to process for string replacement. Add more if needed.
    # Be very careful with broad replacement on .tex, .raw, .bmp, .scc if they are binary.
    # For safety, only process .script, .rsr by default for text replacement.
    # If others are text and need replacement, add them.
    text_file_extensions_for_replace = ['.script', '.rsr'] # More controlled list
    clone_and_rename(src_full_path, dst_mission_path, old_mission_id_raw_basename, new_mission_id,
                     text_file_extensions_for_replace)

    # 2) Prune old scripts & rename content file
    fix_content_and_strings(dst_mission_path, old_mission_id_raw_basename, new_mission_id)

    # 3) Generate new .rsr, _Strings.script and Mission.script
    template_mission_script_full_path = os.path.join(src_full_path, "Mission.script")

    write_rsr(abs_install_path, new_mission_id, title_raw, briefing_raw, objectives_raw) # Pass raw for RSR specific escaping
    write_strings_script(dst_mission_path, new_mission_id, title_script_esc, briefing_script_esc, orders_script_esc, objectives_script_esc)
    update_mission_script(dst_mission_path, new_mission_id, objectives_raw, template_mission_script_full_path)

    # 4) Patch in-game menu and editor menu
    game_menu_script = os.path.join(abs_install_path, 'Scripts', 'Menus', 'MissionsMenu.script')
    mission_class_entry = f'"C{new_mission_id}Mission"' # For game menu
    array_to_patch_game = 'USSR_Missions' if campaign == 'ussr' else 'Germany_Missions'
    patch_array_file(game_menu_script, array_to_patch_game, mission_class_entry)

    editor_menu_script = os.path.join(abs_install_path, 'Scripts', 'Editor', 'MenuConfig.script')
    # Title for editor menu needs to be a script string literal
    editor_mission_entry = f'["{escape_script_string(title_raw)}", "C{new_mission_id}Mission"]'
    patch_array_file(editor_menu_script, 'MissionLoadList', editor_mission_entry)

    print(f"Mission '{new_mission_id}' (Title: '{title_raw}') built successfully at {dst_mission_path}")