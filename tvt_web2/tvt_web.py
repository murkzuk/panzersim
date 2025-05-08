from flask import Flask, render_template, request
from markupsafe import Markup # Import Markup from markupsafe
import os
import re # For sanitizing new_name
from mission_builder import build_mission, sanitize_identifier # Import new helper

app = Flask(__name__)

# Adjust these to your install & missions path:
INSTALL_PATH = r"M:\T34vsTiger" # Use raw string for paths
MISSION_BASE_FOLDER_NAME = "MyMission" # e.g., the 'MyMission' part of 'Missions\MyMission'
MISSION_ROOT = os.path.join(INSTALL_PATH, "Missions", MISSION_BASE_FOLDER_NAME)


def get_existing_missions():
    if not os.path.isdir(MISSION_ROOT):
        return []
    return sorted([ # Sort for consistent UI
        d for d in os.listdir(MISSION_ROOT)
        if os.path.isdir(os.path.join(MISSION_ROOT, d)) and not d.startswith('.') # Avoid hidden dirs
    ])

@app.route("/", methods=["GET", "POST"])
def form():
    message = ""
    message_is_error = False # For styling
    missions = get_existing_missions()

    if request.method == "POST":
        data = request.form

        source_template = data.get("source", "").strip()
        new_name_raw = data.get("new_name", "").strip()
        title_raw = data.get("title", "").strip()
        briefing_raw = data.get("briefing","").strip()
        orders_raw = data.get("orders","").strip()
        
        objectives_raw = [
            data.get(f"obj{i}","").strip()
            for i in range(1, 6) # Max 5 objectives
        ]
        objectives_raw = [o for o in objectives_raw if o] # Filter out empty ones

        campaign = data.get("campaign", "ussr") # Default to ussr if not provided
        editor_mode = "editor" in data

        # --- Input Validation ---
        if not source_template:
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
        elif len(title_raw) > 100: # Arbitrary limit
            message = "❌ Error: Mission Title is too long."
            message_is_error = True
        # Add more validation as needed (e.g., for briefing length, objectives count/length)

        if not message: # If no validation errors so far
            try:
                # The source_folder for build_mission should be relative to INSTALL_PATH/Missions
                # e.g., "MyMission/TemplateName"
                source_folder_for_builder = os.path.join(MISSION_BASE_FOLDER_NAME, source_template)

                build_mission(
                    install_path=INSTALL_PATH,
                    source_folder_relative=source_folder_for_builder,
                    new_mission_name_raw=new_name_raw, # Pass raw, builder will sanitize for path/class
                    title_raw=title_raw,
                    briefing_raw=briefing_raw,
                    orders_raw=orders_raw,
                    objectives_raw=objectives_raw,
                    campaign=campaign,
                    editor_mode=editor_mode
                )
                # Use sanitized name in success message if desired, or raw.
                # For display, HTML escape any user input. Flask/Jinja2 does this by default with {{ }}
                # but if constructing HTML in Python, use Markup.escape or similar.
                # Here, new_name_raw is fine as Jinja will escape it.
                # If you use the sanitized ID:
                # clean_new_name = sanitize_identifier(new_name_raw)
                message = f"✅ Mission '{new_name_raw}' (folder: '{sanitize_identifier(new_name_raw)}') created successfully."

            except FileNotFoundError as e:
                message = f"❌ Error: A required file or folder was not found. {e}"
                message_is_error = True
            except FileExistsError as e:
                message = f"❌ Error: The mission folder to be created already exists. {e}"
                message_is_error = True
            except ValueError as e: # For custom validation errors from builder
                message = f"❌ Error: Invalid input. {e}"
                message_is_error = True
            except Exception as e:
                # Log the full error for debugging on the server
                app.logger.error(f"Mission creation failed: {e}", exc_info=True)
                message = f"❌ Error: An unexpected problem occurred during mission creation. Details: {e}"
                message_is_error = True

    # For rendering, ensure `message` is properly escaped if it contains user input.
    # Jinja2's {{ message }} does this automatically.
    return render_template("form.html",
                           missions=missions,
                           message=message,
                           message_is_error=message_is_error, # For conditional styling
                           # Pass back form data to repopulate on error (optional)
                           form_data=request.form if request.method == "POST" and message_is_error else {}
                           )

if __name__ == "__main__":
    # For development: app.run(debug=True, host="127.0.0.1", port=5000)
    # For "production" local use:
    app.run(debug=False, host="127.0.0.1", port=5000)