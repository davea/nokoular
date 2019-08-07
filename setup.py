from setuptools import setup

APP = ["Nokoular.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "plist": {
        "LSUIElement": True,
        "NSUserNotificationAlertStyle": "alert",
        "CFBundleIdentifier": "me.davea.nokoular",
    },
    "packages": ["rumps", "humanfriendly", "requests"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
