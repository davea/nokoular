from setuptools import setup

APP = ["Nokoular.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "plist": {
        # "LSUIElement": True, # Monterey doesn't let you access Bluetooth with this, sigh.
        "NSUserNotificationAlertStyle": "alert",
        "CFBundleIdentifier": "me.davea.nokoular",
        "NSBluetoothAlwaysUsageDescription": "This app uses Bluetooth",
        "NSBluetoothPeripheralUsageDescription": "This app uses Bluetooth peripherals",
    },
    "packages": ["rumps", "humanfriendly", "requests"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
