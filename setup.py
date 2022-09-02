from setuptools import setup

APP = ["Nokoular.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "plist": {
        # "LSUIElement": True, # Monterey doesn't let you access Bluetooth with this, sigh.
        "NSUserNotificationAlertStyle": "alert",
        "CFBundleIdentifier": "me.davea.nokoular",
        "NSBluetoothAlwaysUsageDescription": "To connect to Timeular Zei",
        "NSBluetoothPeripheralUsageDescription": "To connect to Timeular Zei",
    },
    "packages": ["rumps", "humanfriendly", "requests"],
    "iconfile": "Nokoular.icns",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
