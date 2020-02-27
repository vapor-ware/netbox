from dcim.models import Interface, Device, DeviceRole

from ruamel.yaml import YAML
from pathlib import Path

import sys


file = Path('/opt/netbox/initializers/interfaces.yml')
if not file.is_file():
    sys.exit()

with file.open('r') as stream:
    yaml = YAML(typ='safe')
    config = yaml.load(stream)

    device_role = DeviceRole.objects.get(slug=config.get('device_role'))

    if not device_role:
        sys.exit()

    network_lockers = Device.objects.all().filter(device_role=device_role.id)

    for locker in network_lockers:
        i = 1
        while i < 24:
            strand0 = i
            strand1 = i + 1
            name = '{}-{}'.format(strand0, strand1)

            i += 2

            interface, created = Interface.objects.get_or_create(name=name, device=locker, type='keystone')
            if created:
                print("🔗 Created interface {} for {}".format(interface.name, locker.name))
