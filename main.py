"""
Calculate Activity - Standalone GTK4 Entry Point

This script launches the Calculate activity as a standalone GTK4 application.
It provides a simple ActivityHandle class for compatibility.

Run with: GDK_BACKEND=x11 python3 main.py
"""

import sys
import os
import gi
import cairo

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

gi.require_foreign("cairo")

# Set up standalone environment
os.environ.setdefault("SUGAR_BUNDLE_ID", "org.sugarlabs.Calculate")
os.environ.setdefault("SUGAR_BUNDLE_NAME", "Calculate")
os.environ.setdefault("SUGAR_BUNDLE_PATH", os.getcwd())
os.environ.setdefault("SUGAR_ACTIVITY_ROOT", os.path.expanduser("~/.sugar/default/org.sugarlabs.Calculate"))

activity_root = os.environ["SUGAR_ACTIVITY_ROOT"]
for subdir in ["tmp", "instance", "data"]:
    os.makedirs(os.path.join(activity_root, subdir), exist_ok=True)

# ActivityHandle: Simple container for activity metadata
class ActivityHandle:
    """
    Activity handle for standalone GTK4 execution.
    Provides minimal attributes required by activity initialization.
    """
    def __init__(self, activity_id=None, object_id=None):
        self.activity_id = activity_id or "calculate-activity"
        self.object_id = object_id or "calculate-instance"

from calculate import Calculate

def main():
    """Launch Calculate activity as a standalone GTK4 application."""
    def on_activate(app):
        # Initialize GTK before creating any widgets
        Gtk.init()
        
        # Create activity handle and launch application
        handle = ActivityHandle()
        try:
            activity = Calculate(handle)
            
            # Get the actual Gtk.Window from the activity
            if hasattr(activity, 'get_window'):
                win = activity.get_window()
            elif hasattr(activity, '_window'):
                # For fallback Activity wrapper
                win = activity._ensure_window()
            else:
                # Assume activity itself is the window (shouldn't happen)
                win = activity
            
            # Set up icon theme after window creation (suppress GTK warnings if display unavailable)
            def on_window_realized(widget):
                try:
                    display = Gdk.Display.get_default()
                    if display is not None:
                        icon_theme = Gtk.IconTheme.get_for_display(display)
                        if icon_theme is not None:
                            icon_path = os.path.join(os.getcwd(), "icons")
                            if os.path.exists(icon_path):
                                icon_theme.add_search_path(icon_path)
                except Exception:
                    # Silently skip icon theme setup if it fails
                    pass
            
            win.connect("realize", on_window_realized)
            
            app.add_window(win)
            win.present()
        except Exception as e:
            print("Failed to launch Calculate activity: %s" % e, file=sys.stderr)
            import traceback
            traceback.print_exc()
            app.quit()

    app = Gtk.Application(application_id="org.sugarlabs.Calculate")
    app.connect("activate", on_activate)
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())