from os.path import expanduser

import objc
from Foundation import NSObject

import StreamDeckLayoutManager


class Deck(NSObject):
    _delegate = None
    _manager = None

    def initWithDelegate_(self, delegate):
        self._delegate = delegate
        self._manager = StreamDeckLayoutManager.Manager(
            expanduser("~/.config/Nokoular/nokodeck.toml")
        )
        self._manager.setCallback("key_press", self.key_press_callback)
        self._manager.displayPage("MainPage")
        delegate.deck_didChangeConnectionState_(self, True)
        return self

    def key_press_callback(self, args, key_index):
        self.pyobjc_performSelectorOnMainThread_withObject_waitUntilDone_("updateTimerWithArgs:", [args, key_index], False)

    def updateTimerWithArgs_(self, args):
        (project, tags) = args[0]
        key_index = args[1]

        project = None if not project else project
        self._delegate.deck_didReceiveButtonPress_(self, key_index, project, tags)

    def __del__(self):
        if self._manager:
            self._manager.setBrightness(0)
            self._manager.shutdown()
