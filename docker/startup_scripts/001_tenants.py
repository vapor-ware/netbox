from tenancy.models import Tenant
from ruamel.yaml import YAML
from pathlib import Path
import sys

file = Path('/opt/netbox/initializers/tenants.yml')
if not file.is_file():
  sys.exit()

with file.open('r') as stream:
  yaml = YAML(typ='safe')
  tenants = yaml.load(stream)

  if tenants is not None:
    for params in tenants:

      tenant, created = Tenant.objects.update_or_create(name=params['name'], defaults=params)

      if created:
        print("🏠 Created tenant", tenant.name)
