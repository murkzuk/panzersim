import os
import shutil
import re

# --- Constants based on your Checklist & common practice ---
# SCRIPT_ENCODING = 'cp1252' # Try this first for .script files ("ansi" for Western Windows)
SCRIPT_ENCODING = 'utf-8' # Or try UTF-8 if cp1252 causes issues with special chars & game supports it. Your argparse script used this.
SCRIPT_ERROR_HANDLING = 'replace' # Or 'ignore' if 'replace' causes too many '?' chars

# RSR_ENCODING = 'cp1252' # Your Phase2 script uses "ansi"
RSR_ENCODING = 'utf-8'   # Your argparse script uses "utf-8". Often UTF-16 for RSR too. Let's try utf-8 first.
# RSR_ENCODING = 'utf-16' # If utf-8/cp1252 fails for RSR

# --- Helper Functions ---
def sanitize_identifier(name: str) -> str: # For folder names, class name parts
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if not name: name = "DefaultMission"
    # Ensure it doesn't start with a number if it's for a class name part
    if name[0].isdigit(): name = "_" + name
    return name

def escape_script_wstring(text: str) -> str: # For L"..." strings
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def escape_rsr_string(text: str) -> str: # For "..." in RSR
    return text.replace('"', '""').replace('\n', '\\n') # RSR often uses literal \n

def get_template_value(template_script_path: str, variable_name: str) -> str | None:
    try:
        with open(template_script_path, 'r', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
            for line in f:
                stripped = line.strip()
                if variable_name in stripped and "=" in stripped:
                    try:
                        val_part = stripped.split('=', 1)[1].strip().rstrip(';')
                        if val_part.startswith('L"') and val_part.endswith('"'): return val_part[2:-1]
                        if val_part.startswith('"') and val_part.endswith('"'): return val_part[1:-1]
                        return val_part # For non-string values like booleans, if ever needed
                    except IndexError: continue
        return None
    except FileNotFoundError: return None

# --- Main Builder Function ---
def build_mission(install_path: str, source_folder_relative: str, new_mission_name_raw: str, 
                  title_raw: str, briefing_raw: str, orders_raw: str, objectives_raw: list[str], 
                  campaign: str, editor_mode=False):

    # 1. Resolve Paths and Names
    new_name_clean = sanitize_identifier(new_mission_name_raw) # This is "YourMissionName" from checklist

    abs_install_path = os.path.abspath(install_path)
    src_full_path = os.path.join(abs_install_path, 'Missions', source_folder_relative)
    src_full_path = os.path.abspath(src_full_path)

    if not os.path.isdir(src_full_path):
        raise FileNotFoundError(f"Source mission folder not found: {src_full_path}")

    old_name_from_folder = os.path.basename(src_full_path) # This is "OldMissionName"

    # Destination: new mission folder created alongside the source's parent, or at same level
    dst_mission_folder_base = os.path.dirname(src_full_path)
    dst_mission_folder_full = os.path.join(dst_mission_folder_base, new_name_clean)

    if os.path.exists(dst_mission_folder_full):
        raise FileExistsError(f"Destination folder already exists: {dst_mission_folder_full}")

    print(f"DEBUG: Install Path: {abs_install_path}")
    print(f"DEBUG: Source Path: {src_full_path}")
    print(f"DEBUG: Old Name (from folder): {old_name_from_folder}")
    print(f"DEBUG: New Name (clean): {new_name_clean}")
    print(f"DEBUG: Destination Path: {dst_mission_folder_full}")

    # 2. Clone Folder Structure and Files
    shutil.copytree(src_full_path, dst_mission_folder_full)
    print(f"DEBUG: Cloned '{src_full_path}' to '{dst_mission_folder_full}'")

    # 3. Process Cloned Files
    # Regex for targeted renaming: OldNameMission, OldNameContent, OldNameMission_Strings
    # \b is word boundary
    class_rename_pattern = re.compile(
        rf"\b{re.escape(old_name_from_folder)}(Mission|Content|Mission_Strings)\b",
        re.IGNORECASE # Be a bit flexible with case in template files if needed
    )

    files_processed_for_rename = 0
    for root, _, files in os.walk(dst_mission_folder_full):
        for fname in files:
            if fname.endswith('.script'): # Only process .script files for these class name changes
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                        content = f.read()
                    
                    # Targeted replacement function for the regex
                    def replacer(match_obj):
                        # match_obj.group(0) is the full matched string e.g., "OldNameMission"
                        # match_obj.group(1) is "Mission", "Content", or "Mission_Strings"
                        # We want to replace "OldName" part with "NewName"
                        return new_name_clean + match_obj.group(1)

                    new_content = class_rename_pattern.sub(replacer, content)

                    if new_content != content:
                        with open(fpath, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                            f.write(new_content)
                        files_processed_for_rename += 1
                except Exception as e:
                    print(f"Warning: Error processing {fpath} for class rename: {e}")
    print(f"DEBUG: Processed {files_processed_for_rename} .script files for class name replacements.")

    # Rename specific files: *Content.script and delete old *Mission_Strings.script
    # (New _Strings.script will be generated)
    old_content_script_name = f"{old_name_from_folder}Content.script" # Case from folder name
    new_content_script_name = f"{new_name_clean}Content.script"
    path_old_content = None
    for fname_iter in os.listdir(dst_mission_folder_full): # Find content script with flexible case
        if fname_iter.lower() == old_content_script_name.lower():
            path_old_content = os.path.join(dst_mission_folder_full, fname_iter)
            break
    
    if path_old_content and os.path.exists(path_old_content):
        path_new_content = os.path.join(dst_mission_folder_full, new_content_script_name)
        os.rename(path_old_content, path_new_content)
        print(f"DEBUG: Renamed {path_old_content} to {path_new_content}")
    else:
        print(f"Warning: Original content script like '{old_content_script_name}' not found in {dst_mission_folder_full}.")

    old_strings_script_name = f"{old_name_from_folder}Mission_Strings.script"
    path_old_strings = None
    for fname_iter in os.listdir(dst_mission_folder_full): # Find with flexible case
         if fname_iter.lower() == old_strings_script_name.lower():
            path_old_strings = os.path.join(dst_mission_folder_full, fname_iter)
            break
    if path_old_strings and os.path.exists(path_old_strings):
        os.remove(path_old_strings)
        print(f"DEBUG: Removed old strings script: {path_old_strings}")
    else:
        print(f"Warning: Original strings script like '{old_strings_script_name}' not found for removal.")


    # 4. Generate/Overwrite Key Mission Files (based on Checklist)

    # --- Mission.script ---
    # (Class CYourMissionNameMission, constructor calls YourMissionNameContent)
    path_mission_script = os.path.join(dst_mission_folder_full, "Mission.script")
    template_mission_script_path = os.path.join(src_full_path, "Mission.script") # Original template's Mission.script

    # Get values from template if possible
    map_name = get_template_value(template_mission_script_path, "m_TerrainMapTextureName") or "Textures/Default_Map.tex"
    brief_pic = get_template_value(template_mission_script_path, "m_MissionBriefingPicMaterial") or "DefaultBriefingPic"
    time_str = get_template_value(template_mission_script_path, "m_LocalTime") or "14:00:00"
    print(f"DEBUG: Mission.script - Map: '{map_name}', BriefPic: '{brief_pic}', Time: '{time_str}'")

    with open(path_mission_script, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
        f.write(f"class C{new_name_clean}Mission extends CSPMission\n{{\n")
        f.write(f"    // Static strings referenced from _Strings class as per checklist\n")
        f.write(f"    static WString MissionName    = {new_name_clean}Mission_Strings::MissionName;\n") # Checklist: _Strings has MissionName
        f.write(f"    static WString ObjectivesText = {new_name_clean}Mission_Strings::ObjectivesText;\n")
        for i in range(1, len(objectives_raw) + 1):
            f.write(f"    static WString Objective{i:02d}     = {new_name_clean}Mission_Strings::Objective{i:02d};\n")
        f.write("\n")
        f.write(f'    String  m_LocalTime               = "{time_str}";\n')
        f.write(f'    String  m_TerrainMapTextureName   = "{map_name}";\n')
        f.write(f'    static String m_MissionBriefingPicMaterial = "{brief_pic}";\n\n')
        f.write("    Array   m_MissionObjectives = [\n") # Array of WString *names* from this class
        for i in range(1, len(objectives_raw) + 1):
            f.write(f"        Objective{i:02d}{',' if i < len(objectives_raw) else ''}\n")
        f.write("    ];\n\n")
        f.write("    boolean isDebug = true;\n")
        f.write("    Array   m_NavpointsForPlayerMap = []; // Placeholder for editor\n\n")
        f.write(f"    void C{new_name_clean}Mission()\n    {{\n")
        f.write(f'        CSPMission("C{new_name_clean}Mission", "{new_name_clean}Content");\n')
        f.write("    }\n}\n")
    print(f"DEBUG: Generated {path_mission_script}")

    # --- YourMissionNameMission_Strings.script ---
    path_strings_script = os.path.join(dst_mission_folder_full, f"{new_name_clean}Mission_Strings.script")
    title_esc_L = escape_script_wstring(title_raw)
    # Checklist: ObjectivesText in _Strings is the main block.
    # For _Strings.ObjectivesText, use combined briefing & orders.
    strings_objectives_text_combined = briefing_raw.strip() 
    if orders_raw.strip():
        strings_objectives_text_combined += "\n" + orders_raw.strip()
    strings_objectives_text_esc_L = escape_script_wstring(strings_objectives_text_combined)

    with open(path_strings_script, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
        f.write(f"class {new_name_clean}Mission_Strings\n{{\n")
        f.write(f'    static WString MissionName    = L"{title_esc_L}";\n')
        f.write(f'    static WString ObjectivesText = L"{strings_objectives_text_esc_L}";\n')
        for i, obj_text_raw in enumerate(objectives_raw, 1):
            f.write(f'    static WString Objective{i:02d} = L"{escape_script_wstring(obj_text_raw)}";\n')
        f.write("}\n")
    print(f"DEBUG: Generated {path_strings_script}")

    # --- MissionYourMissionName.rsr ---
    # Stored in Resources/ folder, not the mission folder itself.
    resources_dir = os.path.join(abs_install_path, "Resources")
    os.makedirs(resources_dir, exist_ok=True)
    path_rsr = os.path.join(resources_dir, f"Mission{new_name_clean}.rsr")

    rsr_title_esc = escape_rsr_string(title_raw)
    rsr_briefing_esc = escape_rsr_string(briefing_raw) # RSR has explicit BriefingText
    # RSR ObjectivesText is the list of individual objectives from form, \n separated
    rsr_objectives_text_esc = escape_rsr_string("\n".join(objectives_raw))

    with open(path_rsr, 'w', encoding=RSR_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
        f.write(f"[Mission{new_name_clean}]\n\n")
        f.write(f'MissionName    = "{rsr_title_esc}"\n')
        f.write(f'BriefingText   = "{rsr_briefing_esc}"\n')
        f.write(f'ObjectivesText = "{rsr_objectives_text_esc}"\n')
        # Checklist RSR example doesn't show individual ObjectiveXX fields, only combined ObjectivesText.
        # If your game *needs* them in RSR, add them here.
        # for i, obj_text_raw in enumerate(objectives_raw, 1):
        #    f.write(f'Objective{i:02d}    = "{escape_rsr_string(obj_text_raw)}"\n')
    print(f"DEBUG: Generated {path_rsr}")
    
    # 5. Backup and Patch Menu Scripts

    def patch_menu_script(menu_script_path: str, array_name: str, entry_line_content: str, is_complex: bool):
        backup_path = menu_script_path + ".mb.bak" # Unique backup extension
        if not os.path.exists(menu_script_path):
            print(f"Warning: Menu script {menu_script_path} not found. Skipping patch.")
            return False
        
        try:
            shutil.copy2(menu_script_path, backup_path) # copy2 preserves metadata
            with open(menu_script_path, 'r', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error backing up or reading menu script {menu_script_path}: {e}")
            return False

        output_lines = []
        in_array = False
        bracket_level = 0
        inserted = False
        found_array = False
        
        # Determine indent from existing entries if possible
        array_indent = "    " # Default if array is empty or can't determine
        temp_in_array_for_indent = False
        for line_for_indent in lines:
            if temp_in_array_for_indent:
                if line_for_indent.strip() and not line_for_indent.strip().startswith("//"):
                    match = re.match(r"^(\s+)", line_for_indent)
                    if match: array_indent = match.group(1)
                    break # Found indent
            if f"Array {array_name}" in line_for_indent and "[" in line_for_indent:
                temp_in_array_for_indent = True


        for i, line in enumerate(lines):
            stripped = line.strip()
            if not in_array and f"Array {array_name}" in stripped and "[" in stripped:
                in_array = True
                found_array = True
                bracket_level = line.count('[') - line.count(']')
                output_lines.append(line)
                if bracket_level == 0 and stripped.endswith("[]"): # Empty array like: Array X = [];
                    # Insert inside the []
                    insert_pos = line.rfind(']')
                    if insert_pos != -1:
                        indented_entry = f"\n{array_indent}{entry_line_content}\n{line[:insert_pos].rstrip().rsplit(' ',1)[0] if line.strip() != "[]" else array_indent[:-4]}" # Indent new line
                        modified_line = line[:insert_pos] + indented_entry + line[insert_pos:]
                        output_lines[-1] = modified_line
                        inserted = True
                        in_array = False # Handled empty array
                continue

            if in_array:
                bracket_level += line.count('[') - line.count(']')
                if bracket_level == 0: # End of array block
                    # Find last actual entry to insert after, or insert before the '];'
                    # This logic tries to insert before the closing line of the array block.
                    # Requires the array to be formatted with '];' on its own line or similar.
                    insertion_point = -1
                    for j in range(len(output_lines) -1, -1, -1): # Search backwards in output_lines
                        if output_lines[j].strip().startswith("]") and "];" in output_lines[j].strip() : # End of array: ];
                             insertion_point = j
                             break
                        # If not '];', maybe a line ending with ']' if complex, or '"' if simple string array
                        if is_complex and output_lines[j].strip().endswith("],"): # last complex entry in list
                            insertion_point = j + 1
                            break
                        if not is_complex and output_lines[j].strip().endswith('",'): # last string entry in list
                            insertion_point = j + 1
                            break
                    
                    if insertion_point != -1 and not inserted:
                        # Ensure previous actual entry has a comma if needed
                        if insertion_point > 0 and not output_lines[insertion_point-1].strip().endswith(","):
                             # Find the last non-empty, non-comment line before insertion_point
                             for k_prev in range(insertion_point-1, -1, -1):
                                 prev_l_strip = output_lines[k_prev].strip()
                                 if prev_l_strip and not prev_l_strip.startswith("//"):
                                     if not prev_l_strip.endswith(","):
                                         output_lines[k_prev] = output_lines[k_prev].rstrip("\r\n") + ",\n"
                                     break

                        output_lines.insert(insertion_point, array_indent + entry_line_content + ",\n") # Add comma to new entry
                        inserted = True
                    elif not inserted: # Fallback if specific structure not found
                        print(f"Warning: Could not find standard insertion point for {array_name}, appending inside.")
                        # Try to insert just before the line that closes the array, if identified
                        closing_line_idx = -1
                        for k_cls in range(len(output_lines)-1, -1, -1):
                            if output_lines[k_cls].strip().startswith("]") and ";" in output_lines[k_cls]:
                                closing_line_idx = k_cls
                                break
                        if closing_line_idx != -1:
                             output_lines.insert(closing_line_idx, array_indent + entry_line_content + ",\n")
                             inserted = True


                    in_array = False # Reset
                output_lines.append(line)
            else:
                output_lines.append(line)
        
        if not found_array:
            print(f"Warning: Array '{array_name}' not found in {menu_script_path}.")
            return False
        if not inserted:
            print(f"Warning: Failed to insert entry into '{array_name}' in {menu_script_path}. Manual edit may be required.")
            # Fallback: append to end of file if all else fails (bad idea usually)
            # output_lines.append(array_indent + entry_line_content + ",\n")
            return False # Indicate failure to insert

        try:
            with open(menu_script_path, 'w', encoding=SCRIPT_ENCODING, errors=SCRIPT_ERROR_HANDLING) as f:
                f.writelines(output_lines)
            print(f"DEBUG: Patched {menu_script_path} for array {array_name}.")
            return True
        except Exception as e:
            print(f"Error writing patched menu script {menu_script_path}: {e}")
            return False

    # --- Patch MissionsMenu.script ---
    # Checklist entry: [ "Resources/MissionFile.rsr", new #MissionCSPData<CClassNameMission>(), 0 ],
    game_menu_path = os.path.join(abs_install_path, 'Scripts', 'Menus', 'MissionsMenu.script')
    game_menu_array = 'USSR_Missions' if campaign == 'ussr' else 'Germany_Missions'
    game_menu_entry = f'["Resources/Mission{new_name_clean}.rsr", new #MissionCSPData<C{new_name_clean}Mission>(), 0]' # No trailing comma here, patcher adds if needed
    patch_menu_script(game_menu_path, game_menu_array, game_menu_entry, is_complex=True)

    # --- Patch MenuConfig.script (Editor) ---
    # Entry: [ "Mission Title", "CClassNameMission" ],
    editor_menu_path = os.path.join(abs_install_path, 'Scripts', 'Editor', 'MenuConfig.script')
    editor_menu_array = 'MissionLoadList' # Common name for editor mission list
    editor_menu_entry = f'["{escape_script_wstring(title_raw)}", "C{new_name_clean}Mission"]' # No trailing comma
    patch_menu_script(editor_menu_path, editor_menu_array, editor_menu_entry, is_complex=True)

    print(f"\n--- Mission '{title_raw}' (folder: {new_name_clean}) build process finished. ---")
    print("Please check console for DEBUG messages, warnings, and errors.")
    print("Verify generated files and test in-game.")