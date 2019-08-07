import sys
import threading
import logging

import objc
from PyObjCTools import AppHelper
from Foundation import NSObject

objc.loadBundle(
    "CoreBluetooth",
    globals(),
    bundle_path=objc.pathForFramework(
        "/System/Library/Frameworks/IOBluetooth.framework/Versions/A/Frameworks/CoreBluetooth.framework"
    ),
)


SERVICE_UUID = "C7E70010-C847-11E6-8175-8C89A55D403C"
CHAR_UUID = "C7E70012-C847-11E6-8175-8C89A55D403C"


class Zei(NSObject):
    _delegate = None

    _centralManager = None
    _peripheral = None

    _orientation = -1
    _connected = False

    def initWithDelegate_(self, delegate):
        super().init()
        self._delegate = delegate
        self._centralManager = CBCentralManager.alloc().initWithDelegate_queue_(
            self, None
        )

        return self

    def centralManagerDidUpdateState_(self, manager):
        """Called when the BLE adapter is powered on and ready to scan/connect
        to devices.
        """
        logging.debug(
            f"centralManagerDidUpdateState called {self._centralManager.state()}"
        )
        if self._centralManager.state() == 5:
            self.connect()

    def connect(self):
        if self._centralManager.state() != 5:
            logging.debug("not scanning; adapter not powered on")
            return
        logging.debug("starting scan")
        self._centralManager.scanForPeripheralsWithServices_options_(None, None)
        logging.debug("scan started")

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
        self, manager, peripheral, data, rssi
    ):
        if peripheral.name() == "Timeular ZEI":
            self._peripheral = peripheral
            logging.debug(f"Connecting to {peripheral.name()} {data} {rssi}")
            manager.stopScan()
            manager.connectPeripheral_options_(peripheral, None)

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        logging.debug(f"Connected to {peripheral.name()}")
        manager.stopScan()
        peripheral.setDelegate_(self)
        peripheral.discoverServices_([CBUUID.UUIDWithString_(SERVICE_UUID)])
        if self._delegate:
            self._delegate.zei_didChangeConnectionState_(self, True)

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        logging.debug(f"Disconnected {peripheral.name()}")
        if self._delegate:
            self._delegate.zei_didChangeConnectionState_(self, False)

    def centralManager_didUpdatePeripheralConnectionState_(self, manager, peripheral):
        logging.debug("centralManager_didUpdatePeripheralConnectionState_")

    def centralManager_didFailToConnectPeripheral_error_(
        self, manager, peripheral, error
    ):
        logging.debug(f"centralManager_didFailToConnectPeripheral_error_ {error}")

    def centralManager_didFindPeripheral_forType_(self, manager, peripheral, ptype):
        logging.debug(f"centralManager_didFindPeripheral_forType_ {ptype}")

    def centralManager_connectionEventDidOccur_forPeripheral_(
        self, manager, event, peripheral
    ):
        logging.debug(f"centralManager_connectionEventDidOccur_forPeripheral_ {event}")

    def peripheral_didDiscoverServices_(self, peripheral, error):
        logging.debug(f"Found {len(peripheral.services())} services")
        for service in peripheral.services():
            peripheral.discoverCharacteristics_forService_(
                [CBUUID.UUIDWithString_(CHAR_UUID)], service
            )

    def peripheral_didDiscoverCharacteristicsForService_error_(
        self, peripheral, service, error
    ):
        """Called when characteristics are discovered for a service."""
        logging.debug("peripheral_didDiscoverCharacteristicsForService_error called")
        for char in service.characteristics():
            peripheral.readValueForCharacteristic_(char)
            peripheral.setNotifyValue_forCharacteristic_(True, char)

    def peripheral_didUpdateValueForCharacteristic_error_(
        self, peripheral, characteristic, error
    ):
        logging.debug("peripheral_didUpdateValueForCharacteristic_error_ called")
        value = characteristic.value().bytes().tobytes()
        orientation = int.from_bytes(value, byteorder="big")
        logging.debug("value: %s %d", value, orientation)

        if self._delegate:
            self._delegate.zei_didUpdateOrientation_(self, orientation)

    def respondsToSelector_(self, selector):
        responds = super().respondsToSelector_(selector)
        logging.debug("%s %s", selector, responds)
        return responds
