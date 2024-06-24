import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = None
        self.include_tx_power = False
        self.data = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids, signature='s')
        if self.solicit_uuids:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids, signature='s')
        if self.manufacturer_data:
            properties['ManufacturerData'] = dbus.Dictionary(self.manufacturer_data, signature='qv')
        if self.service_data:
            properties['ServiceData'] = dbus.Dictionary(self.service_data, signature='sv')
        if self.local_name:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.include_tx_power:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        if self.data:
            properties['Data'] = dbus.Dictionary(self.data, signature='yv')
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dict()
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dict()
        self.service_data[uuid] = dbus.Array(data, signature='y')

       @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='', out_signature='a{sv}')
    def Get(self, interface, prop):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface: ' + interface)
        properties = self.get_properties()
        if prop not in properties[interface]:
            raise dbus.exceptions.DBusException('Invalid property: ' + prop)
        return properties[interface][prop]

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='sas', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface: ' + interface)
        return self.get_properties()[interface]

    @dbus.service.method(dbus_interface=LE_ADVERTISEMENT_IFACE,
                         in_signature='', out_signature='')
    def Release(self):
        pass

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    def get_properties(self):
        return {GATT_MANAGER_IFACE: {}}

    def get_service(self, index):
        return self.services[index]

       @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='', out_signature='a{sv}')
    def Get(self, interface, prop):
        if interface != GATT_MANAGER_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface: ' + interface)
        properties = self.get_properties()
        if prop not in properties[interface]:
            raise dbus.exceptions.DBusException('Invalid property: ' + prop)
        return properties[interface][prop]

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='sas', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_MANAGER_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface: ' + interface)
        return self.get_properties()[interface]

    @dbus.service.method(dbus_interface=dbus.OBJECT_MANAGER_IFACE,
                         in_signature='', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()
        return response

class Service(dbus.service.Object):
    def __init__(self, bus, index, uuid, primary):
        self.path = f"/org/bluez/example/service{index}"
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(self.get_characteristic_paths(), signature='o')
            }
        }

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristics(self):
        return self.characteristics

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.get_path() + f"/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.Object.Path(self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(self.get_descriptor_paths(), signature='o')
            }
        }

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptors(self):
        return self.descriptors

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    @dbus.service.method(dbus_interface=GATT_CHRC_IFACE,
                         in_signature='a{sv}', out_signature='a{sv}')
    def ReadValue(self, options):
        return dbus.Array([], signature='y')

    @dbus.service.method(dbus_interface=GATT_CHRC_IFACE,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        print(f"Received: {bytearray(value).decode()}")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    adapter = bus.get_object(BLUEZ_SERVICE_NAME, '/org/bluez/hci0')
    adapter_props = dbus.Interface(adapter, dbus.PROPERTIES_IFACE)
    adapter_props.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))

    app = Application(bus)

    service = Service(bus, 0, '12345678-1234-5678-1234-56789abcdef0', True)
    app.add_service(service)

    characteristic = Characteristic(bus, 0, '12345678-1234-5678-1234-56789abcdef1', ['read', 'write'], service)
    service.add_characteristic(characteristic)

    bus_name = dbus.service.BusName(BLUEZ_SERVICE_NAME, bus)
    obj = dbus.service.Object(bus, '/org/bluez')

    gatt_manager = bus.get_object(BLUEZ_SERVICE_NAME, '/org/bluez/hci0')
    gatt_manager_props = dbus.Interface(gatt_manager, dbus.PROPERTIES_IFACE)

    gatt_manager_interface = dbus.Interface(gatt_manager, GATT_MANAGER_IFACE)
    gatt_manager_interface.RegisterApplication(app.get_path(), {},
                                               reply_handler=print("GATT application registered successfully"),
                                               error_handler=print("Failed to register GATT application"))

    ad_manager = bus.get_object(BLUEZ_SERVICE_NAME, '/org/bluez/hci0')
    ad_manager_props = dbus.Interface(ad_manager, dbus.PROPERTIES_IFACE)

    ad_manager_interface = dbus.Interface(ad_manager, LE_ADVERTISING_MANAGER_IFACE)
    advertisement = Advertisement(bus, 0, 'peripheral')
    advertisement.add_service_uuid(service.uuid)

    ad_manager_interface.RegisterAdvertisement(advertisement.get_path(), {},
                                               reply_handler=print("Advertisement registered successfully"),
                                               error_handler=print("Failed to register advertisement"))

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
