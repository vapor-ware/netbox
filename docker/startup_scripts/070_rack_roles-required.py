from dcim.models import RackRole
from ruamel.yaml import YAML
from utilities.choices import ColorChoices

from pathlib import Path
import sys

file = Path('/opt/netbox/initializers/rack_roles.yml')
if not file.is_file():
  sys.exit()

with file.open('r') as stream:
  yaml=YAML(typ='safe')
  rack_roles = yaml.load(stream)

  if rack_roles is not None:
    for params in rack_roles:
      if 'color' in params:
        color = params.pop('color')

        for color_tpl in ColorChoices:
          if color in color_tpl:
            params['color'] = color_tpl[0]

      rack_role, created = RackRole.objects.update_or_create(name=params['name'], defaults=params)

      if created:
        print("🎨 Created rack role", rack_role.name)
