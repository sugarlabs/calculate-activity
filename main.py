#!/usr/bin/env python3

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

from sugar4.activity.activityhandle import ActivityHandle
from calculate import Calculate

def main():
    def on_activate(app):
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_search_path(os.path.join(os.getcwd(), "icons"))

        handle = ActivityHandle(
            activity_id="calculate-local",
            object_id="calculate-local"
        )
        try:
            win = Calculate(handle)
            app.add_window(win)
            win.present()
        except Exception as e:
            print("Failed to launch activity: %s" % e, file=sys.stderr)
            app.quit()

    app = Gtk.Application(application_id="org.sugarlabs.Calculate.local")
    app.connect("activate", on_activate)
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())