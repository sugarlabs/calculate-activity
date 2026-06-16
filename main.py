#!/usr/bin/env python3

import sys
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

# ---- Setup Sugar environment ----
os.environ.setdefault("SUGAR_BUNDLE_ID", "org.sugarlabs.Calculate")
os.environ.setdefault("SUGAR_BUNDLE_NAME", "Calculate")
os.environ.setdefault("SUGAR_BUNDLE_PATH", os.getcwd())
os.environ.setdefault("SUGAR_ACTIVITY_ROOT", os.path.join(os.path.expanduser("~"), ".sugar", "default", "org.sugarlabs.Calculate"))

# Create activity directories if they don't exist
activity_root = os.environ["SUGAR_ACTIVITY_ROOT"]
for subdir in ["tmp", "instance", "data"]:
    path = os.path.join(activity_root, subdir)
    os.makedirs(path, exist_ok=True)


from sugar4.activity.activityhandle import ActivityHandle
from calculate import Calculate


def main(argv=None):
    argv = argv or sys.argv
    
    # Keep reference to activity to prevent garbage collection
    activity_ref = None

    def on_activate(app):
        nonlocal activity_ref
        
        # Create ActivityHandle for local run
        handle = ActivityHandle(
            activity_id="calculate-local",
            object_id="calculate-local"
        )

        try:
            # Create activity (Activity creates its own window)
            activity_ref = Calculate(handle)
            
            # Add the activity window to the application
            app.add_window(activity_ref)
            
            # Show the window
            activity_ref.show()
            
            # Present the window (GTK4)
            activity_ref.present()
            
        except Exception as e:
            print(f"Error creating activity: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            app.quit()

    app = Gtk.Application(application_id="org.sugarlabs.Calculate.local")
    app.connect("activate", on_activate)
    
    # Keep application running until window is closed
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main())
