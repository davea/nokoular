import logging
from datetime import datetime, timedelta
from textwrap import shorten

import rumps
from humanfriendly import format_timespan

from noko import Noko
from timeular import Zei

from config import NOKO_TOKEN, ORIENTATION_MAPPING

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s",
)

log = logging.getLogger(__name__)

rumps.debug_mode(True)

app = None


class NokoularApp(rumps.App):
    zei = None
    noko = None

    _current_state = None
    _description_window = None

    def __init__(self):
        super().__init__("Z:!")
        self.menu = ["Not logging", "..."]
        self.zei = Zei.alloc().initWithDelegate_(self)
        self.noko = Noko(NOKO_TOKEN)
        self._setup_windows()

    def _setup_windows(self):
        self._description_window = rumps.Window(
            title="Description", cancel=True, dimensions=(320, 40)
        )

        self._project_window = rumps.Window(
            title="Which project?",
            dimensions=(320, 40),
            options=self.noko.projects.keys(),
            options_empty="-- Select a project --",
        )

    @rumps.clicked("Save entry...")
    def save_entry(self, _):
        # Forces the current entry to be saved and the timer stopped
        # Acts as if the Zei has been upended to pause tracking.
        self.zei_didUpdateOrientation_(self.zei, 0)

    @rumps.clicked("...")
    def set_description(self, _):
        project, description, start_time = self._current_state
        self._description_window.title = f"Project: {project}"
        self._description_window.default_text = description
        response = self._description_window.run()
        if response.clicked:
            self.noko.set_timer_description(project, response.text)
            self._current_state = (project, response.text, start_time)
            self.update_menu_titles()

    def update_menu_titles(self):
        if self._current_state is None:
            project, description, start_time = (None, None, None)
        else:
            project, description, start_time = self._current_state

        description = description or "---"
        project = project or "Not logging"

        self.menu.values()[0].title = project
        self.menu.values()[1].title = shorten(
            description, len(project), placeholder="..."
        )

    def start_timer_for_project(self, project, tags):
        if project == "<Other>":
            # Zei is upside down, which is a special state to indicate
            # no specific project has been assigned, so ask the user what
            # project it is
            response = self._project_window.run()
            project = response.option
            if response.text:
                tags = response.text.strip()
            if project == "-- Select a project --":
                project = None

        start_time = datetime.utcnow()

        if project:
            log.debug(f"project is {project}, starting timer")
            running_seconds, tags = self.noko.start_timer(project, description=tags)
            start_time -= timedelta(seconds=running_seconds)

        self._current_state = (project, tags, start_time)
        self.update_menu_titles()

    def save_timer_for_project(self, project, description):
        self.noko.stop_timer(project, description)

    def switch_timer(self, old_project, description, new_project, new_tags):
        self.save_timer_for_project(old_project, description)
        self.start_timer_for_project(new_project, new_tags)

    def zei_didUpdateOrientation_(self, zei, orientation):
        self.title = f"Z:{orientation}"

        new_project, new_tags = ORIENTATION_MAPPING[orientation]

        # if the Zei has been rotated from a side with a project/tags associated,
        # need to capture info from the user and stop the timer on Noko.
        # Once that's done we need to start a timer for the new side

        if self._current_state is None:
            # it's the first time we've been called, so all we need to do is
            # set the current state and start a timer for this side.
            log.debug("first call, starting timer for the first time")
            self.start_timer_for_project(new_project, new_tags)
        else:
            # we've moved away from an project which needs to have its time logged
            old_project, old_tags, old_start_time = self._current_state

            log.debug(f"Just moved away from side {self._current_state}")

            # if the old_project is None then it's not a side of the Zei which
            # has a project associated, so we don't need to do any notification
            # just start the timer for the new project
            if old_project is None:
                log.debug(
                    "old_project is None, no timer to stop, and not showing notification."
                )
                self.start_timer_for_project(new_project, new_tags)
            else:
                # we need to show a notification for the log which we've just
                # moved away from, to capture any tags and description from
                # the user.

                log.debug(f"old_project is not None: {old_project}")

                elapsed = datetime.utcnow() - old_start_time
                log.debug("showing notification")
                rumps.notification(
                    f"Log {format_timespan(elapsed)}",
                    f"Project: {old_project}",
                    f"Description: {old_tags}",
                    placeholder=old_tags,
                    data={
                        "old_project": old_project,
                        "old_tags": old_tags,
                        "new_project": new_project,
                        "new_tags": new_tags,
                    },
                    has_reply_button=True,
                )

    def zei_didChangeConnectionState_(self, zei, connected):
        self.title = "Z:OK" if connected else "Z:!"


@rumps.notifications
def notification_handler(data):
    log.debug(f"notification_handler: {data}")
    description = data["response"].string() if data["response"] else ""
    if data["old_tags"]:
        description = f"{data['old_tags']} {description}"
    app.switch_timer(
        data["old_project"], description, data["new_project"], data["new_tags"]
    )


def main():
    global app
    app = NokoularApp()
    app.run()


if __name__ == "__main__":
    main()
