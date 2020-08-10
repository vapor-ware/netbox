"""
    Automate cabling process so that all Customer Network Locker's 1-2 interfaces go to Access Switch's EFR1, and 3-4 ones go to EFR2.
    This script should only be run once and in dev environment. Mostly used for integration testing purposes.
"""

from dcim.models import Cable

from ruamel.yaml import YAML
from pathlib import Path

import sys


def get_devices(role):
    from dcim.models import Device, DeviceRole

    return Device.objects.all().filter(device_role=DeviceRole.objects.get(slug=role).id)


file = Path('/opt/netbox/initializers/cables.yml')
if not file.is_file():
    sys.exit()

with file.open('r') as stream:
    yaml = YAML(typ='safe')
    config = yaml.load(stream)

    if config.get('cable_interfaces'):
        lockers = get_devices('customer-network-locker')
        switches = get_devices('access-switch')

        i = 0
        for locker in lockers:
            # break if i is larger than switch interface's size.
            if i > len(switches[0].vc_interfaces)-1:
                break

            i12 = locker.vc_interfaces[0]
            i34 = locker.vc_interfaces[1]

            efr1 = switches[0].vc_interfaces[i]
            efr2 = switches[1].vc_interfaces[i]

            c1 = Cable.objects.create(termination_a=i12, termination_b=efr1)
            print('🔌 Created cable for {} and {}'.format(i12.name, efr1.name))

            c2 = Cable.objects.create(termination_a=i34, termination_b=efr2)
            print('🔌 Created cable for {} and {}'.format(i34.name, efr2.name))

            i += 1
