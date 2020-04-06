from dcim.models import Interface, Device, DeviceRole

from ruamel.yaml import YAML
from pathlib import Path

import sys


def template_customer_locker(devices, port_count):
    from dcim.models import Interface

    for locker in devices:
        i = 1
        while i < 24:
            strand0 = i
            strand1 = i + 1
            name = '{}-{}'.format(strand0, strand1)

            i += 2

            interface, created = Interface.objects.get_or_create(name=name, device=locker, type='keystone')
            if created:
                print("🔗 Created interface {} for {}".format(interface.name, locker.name))


def template_efr(devices, port_count):
    from dcim.models import Interface

    for switch in devices:
        i = 1
        while i <= port_count:
            interface, created = Interface.objects.get_or_create(name=f'xe-0/0/{i}', device=switch, type='10gbase-x-sfpp')
            i += 1
            if created:
                print("🔗 Created interface {} for {}".format(interface.name, switch.name))


templates = {
    'efr': template_efr,
    'customer-locker': template_customer_locker,
}

file = Path('/opt/netbox/initializers/interfaces.yml')
if not file.is_file():
    sys.exit()

with file.open('r') as stream:
    yaml = YAML(typ='safe')
    config = yaml.load(stream)


for c in config:
    device_role = DeviceRole.objects.get(slug=c.get('device_role'))

    if not device_role:
        continue

    interface_template = c.get('template')

    if not interface_template or interface_template not in templates:
        continue

    port_count = c.get('ports', 0)

    devices = Device.objects.all().filter(device_role=device_role.id)

    templates[interface_template](devices, port_count)
