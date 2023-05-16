import logging
from pprint import pprint
from pathlib import Path
import json

import requests

log = logging.getLogger(__name__)


class Noko:
    _session = None
    _projects = None

    def __init__(self, token):
        self._session = requests.Session()
        self._session.headers.update(
            {"User-Agent": "Nokoular/1.0", "X-NokoToken": token}
        )

    def _api(self, endpoint, method="GET", **kwargs):
        url = f"https://api.nokotime.com/v2/{endpoint}"
        # TODO: Handle pagination
        resp = self._session.request(method, url, **kwargs)
        if not resp.ok:
            resp.raise_for_status()
        if resp.status_code != 200:
            return
        return resp.json()

    @property
    def projects(self):
        if not self._projects:
            self._projects = self._load_projects()
        return self._projects

    def _load_projects(self, use_cache=True):
        cache_dir = Path("~/.config/Nokoular/cache").expanduser()
        cache_dir.mkdir(parents=True, exist_ok=True)
        cached = cache_dir / "noko_projects.json"
        if use_cache and cached.exists():
            return json.load(open(cached))
        else:
            projects = {
                p["name"]: p["id"]
                for p in self._api(
                    "projects", params={"enabled": "true", "per_page": 1_000}
                )
            }
            with open(cached, "w") as f:
                json.dump(projects, f)
            return projects

    def refresh_projects(self):
        self._projects = self._load_projects(use_cache=False)

    def start_timer(self, project, description=None):
        pid = self.projects[project]
        log.debug(
            "Starting timer for project %s (%s), description: %s",
            project,
            pid,
            description,
        )
        json = {"description": description} if description else None
        response = self._api(f"projects/{pid}/timer/start", method="PUT", json=json)
        return (response["seconds"], response["description"])

    def stop_timer(self, project, description):
        pid = self.projects[project]
        if "#delete" in description:
            log.debug("Discarding timer for project %s (%s)", project, pid)
            return self._api(f"projects/{pid}/timer", method="DELETE")
        else:
            log.debug(
                "Stopping timer for project %s (%s), description: %s",
                project,
                pid,
                description,
            )
            return self._api(
                f"projects/{pid}/timer/log",
                method="PUT",
                json={"description": description},
            )

    def set_timer_description(self, project, description):
        pid = self.projects[project]
        log.debug(
            "Setting description for project %s (%s): %s", project, pid, description
        )
        return self._api(
            f"projects/{pid}/timer", method="PUT", json={"description": description}
        )
