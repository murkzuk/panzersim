from flask import Flask, render_template, request
from markupsafe import Markup # Import Markup from markupsafe
import os
import re
from mission_builder import build_mission, sanitize_identifier # Assuming mission_builder.py is in the same directory

app = Flask(__name__)

# This will be the name of your custom templates subfolder within the 'Missions' directory
USER_TEMPLATE_SUBFOLDER = "MyMission" # You can change this if your folder is named differently

def get_mission_templates(selected_install_path):
    """
    Recursively scans for mission templates in the selected TvT installation.
    A directory is considered a mission template if it contains "Mission.script".
    Returns a list of dictionaries: [{'display_name': str, 'value_path': str}]
    'value_path' is the path relative to the 'Missions' directory.
    """
    templates = []
    if not selected_install_path or not os.path.isdir(selected_install_path):
        app.logger.warning(f"Invalid or non-existent install path provided: {selected_install_path}")
        return templates

    missions_root_path = os.path.join(selected_install_path, "Missions")
    if not os.path.isdir(missions_root_path):
        app.logger.warning(f"'Missions' directory not found in: {selected_install_path}")
        return templates

    app.logger.info(f"Scanning for mission templates in: {missions_root_path}")

    for root, dirs, files in os.walk(missions_root_path):
        if "Mission.script" in files:
            relative_path = os.path.relpath(root, missions_root_path)
            
            # Normalize path separators for display and internal use
            normalized_relative_path = relative_path.replace(os.sep, '/')

            display_parts = [part for part in normalized_relative_path.split('/') if part and part != '.']
            
            prefix = ""
            # Check if it's under the USER_TEMPLATE_SUBFOLDER
            if normalized_relative_path.lower().startswith(USER_TEMPLATE_SUBFOLDER.lower() + '/') or \
               normalized_relative_path.lower() == USER_TEMPLATE_SUBFOLDER.lower():
                prefix = "[Custom] "
                if display_parts and display_parts[0].lower() == USER_TEMPLATE_SUBFOLDER.lower():
                    display_parts = display_parts[1:] # Remove USER_TEMPLATE_SUBFOLDER from display if present

            display_name = prefix + " / ".join(display_parts)
            if not display_parts: # Handles case like Missions/MyMission itself being a template
                 # Or if relative_path was just USER_TEMPLATE_SUBFOLDER
                base_folder_name = os.path.basename(root) # Get the actual folder name
                if prefix and base_folder_name.lower() == USER_TEMPLATE_SUBFOLDER.lower():
                    display_name = prefix.strip() # Just "[Custom]" might be too vague, use folder name
                    display_name = f"{prefix}{base_folder_name}"
                elif not prefix : # Mission directly in 'Missions' root
                    display_name = base_folder_name


            templates.append({
                "display_name": display_name,
                "value_path": normalized_relative_path
            })
            app.logger.debug(f"Found template: Display='{display_name}', Path='{normalized_relative_path}'")
            
            dirs[:] = [] # Don't look for missions in subdirectories of this identified mission

    templates.sort(key=lambda x: x['display_name'].lower())
    if not templates:
        app.logger.info(f"No mission templates (containing Mission.script) found in {missions_root_path}")
    return templates


@app.route("/", methods=["GET", "POST"])
def form():
    message = ""
    message_is_error = False
    mission_templates = []
    
    default_install_path = r"" # Start with empty, encourage user input. Or set your most common path.
    current_install_path = default_install_path
    form_data_retained = {}

    if request.method == "POST":
        form_data_retained = request.form.copy()
        current_install_path = request.form.get("install_path", "").strip()

        # Always try to load templates if a path is provided or was already there
        if current_install_path:
             mission_templates = get_mission_templates(current_install_path)

        if "load_templates_button" in request.form:
            # This was a "Load Templates" submission
            if not current_install_path:
                 message = "ℹ️ Please enter a TvT Installation Path to load templates."
                 message_is_error = False # Informational
            elif not mission_templates and os.path.isdir(current_install_path):
                 if not os.path.isdir(os.path.join(current_install_path, "Missions")):
                     message = f"ℹ️ Valid path, but 'Missions' subfolder not found in '{current_install_path}'."
                 else:
                     message = f"ℹ️ No mission templates found for path '{current_install_path}'. Ensure templates have a 'Mission.script' file."
                 message_is_error = False # Informational
            elif mission_templates:
                message = f"✅ Templates loaded successfully from '{current_install_path}'."
                message_is_error = False
            # No else needed if path is invalid, get_mission_templates handles logging

        elif "clone_mission_button" in request.form:
            # This was a "Clone Mission" submission
            if not current_install_path or not os.path.isdir(current_install_path):
                message = "❌ Error: TvT Installation Path is missing or invalid. Please set it and load templates first."
                message_is_error = True
                # Return here as we can't proceed without a valid install path for building
                return render_template("form.html",
                                   mission_templates=mission_templates, # Could be empty
                                   message=message,
                                   message_is_error=message_is_error,
                                   form_data=form_data_retained,
                                   current_install_path=current_install_path)

            # Proceed with cloning logic
            source_template_relative_path = request.form.get("source_template_path", "").strip()
            new_name_raw = request.form.get("new_name", "").strip()
            title_raw = request.form.get("title", "").strip()
            briefing_raw = request.form.get("briefing","").strip()
            orders_raw = request.form.get("orders","").strip()
            
            objectives_raw = [
                request.form.get(f"obj{i}","").strip()
                for i in range(1, 6)
            ]
            objectives_raw = [o for o in objectives_raw if o]

            campaign = request.form.get("campaign", "ussr")
            editor_mode = "editor" in request.form

            # --- Input Validation for mission building ---
            if not source_template_relative_path:
                message = "❌ Error: Base Mission to Clone must be selected."
                message_is_error = True
            elif not new_name_raw:
                message = "❌ Error: New Mission Folder Name is required."
                message_is_error = True
            elif not re.match(r'^[a-zA-Z0-9_ .-]{1,50}$', new_name_raw): # Allow spaces, dots, hyphens initially for raw
                message = "❌ Error: New Mission Folder Name has invalid characters or is too long."
                message_is_error = True
            elif not title_raw:
                message = "❌ Error: Mission Title (Menu) is required."
                message_is_error = True
            # Add more validation as needed

            if not message_is_error:
                try:
                    build_mission(
                        install_path=current_install_path,
                        source_folder_relative=source_template_relative_path,
                        new_mission_name_raw=new_name_raw,
                        title_raw=title_raw,
                        briefing_raw=briefing_raw,
                        orders_raw=orders_raw,
                        objectives_raw=objectives_raw,
                        campaign=campaign,
                        editor_mode=editor_mode
                    )
                    sanitized_new_name = sanitize_identifier(new_name_raw)
                    message = f"✅ Mission '{title_raw}' (folder: '{sanitized_new_name}') created successfully in '{current_install_path}'."
                    form_data_retained = {'install_path': current_install_path} # Keep install path, clear other fields
                    # Reload templates for the current path to ensure dropdown is still populated
                    mission_templates = get_mission_templates(current_install_path)
                except FileNotFoundError as e:
                    message = f"❌ Error: A required file/folder was not found. {e}"
                    message_is_error = True
                except FileExistsError as e:
                    message = f"❌ Error: The mission folder to be created already exists. {e}"
                    message_is_error = True
                except ValueError as e:
                    message = f"❌ Error: Invalid input. {e}"
                    message_is_error = True
                except Exception as e:
                    app.logger.error(f"Mission creation failed: {e}", exc_info=True)
                    message = f"❌ Error: An unexpected problem occurred. Check logs. Details: {e}"
                    message_is_error = True
        else:
            # POST without a specific button, maybe user hit Enter in a field.
            # Treat as implicit "load templates" if path is present.
            if not current_install_path:
                message = "ℹ️ Please enter a TvT Installation Path."
            # Templates would have been loaded at the start of POST if path was there.

    elif request.method == "GET":
        current_install_path = request.args.get("install_path", default_install_path).strip()
        form_data_retained = request.args.to_dict() # Allow path to be passed via GET for refresh
        if current_install_path:
            mission_templates = get_mission_templates(current_install_path)
            if not mission_templates and os.path.isdir(current_install_path):
                if not os.path.isdir(os.path.join(current_install_path, "Missions")):
                    message = f"ℹ️ Valid path, but 'Missions' subfolder not found in '{current_install_path}'."
                else:
                    message = f"ℹ️ No mission templates (containing Mission.script) found for path '{current_install_path}'."
                # message_is_error = False # Informational

    # Always ensure current_install_path is passed to template for the input field
    if 'install_path' not in form_data_retained and current_install_path:
        form_data_retained['install_path'] = current_install_path


    return render_template("form.html",
                           mission_templates=mission_templates,
                           message=message,
                           message_is_error=message_is_error,
                           form_data=form_data_retained,
                           current_install_path=current_install_path)

if __name__ == "__main__":
    # For easier debugging of template loading, enable Flask logging
    import logging
    logging.basicConfig(level=logging.DEBUG) # Show DEBUG, INFO, WARNING, ERROR, CRITICAL
    # You can also configure app.logger specifically if preferred.
    
    app.run(debug=True, host="127.0.0.1", port=5000)