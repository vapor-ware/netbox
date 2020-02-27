from django.db import migrations


def interface_type_to_slug(apps, schema_editor):
    Interface = apps.get_model('dcim', 'Interface')
    Interface.objects.filter(type=32766).update(type='keystone')


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0098_devicetype_images'),
    ]

    operations = [
        migrations.RunPython(
            code=interface_type_to_slug
        ),
    ]
