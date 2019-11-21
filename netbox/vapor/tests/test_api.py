from dcim.models import (
    Cable,
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Site,
)
from django.urls import reverse
from rest_framework import status
from tenancy.models import Tenant as Customer
from utilities.testing import APITestCase, create_test_user


class VaporTestCustomers(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.customer1 = Customer.objects.create(name='Test Customer 1', slug='test-customer-1')

    def test_get_a_customer(self):
        """ Inspect a single customer """
        url = reverse('vapor-api:tenant-detail', kwargs={'pk': self.customer1.pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], self.customer1.name)

    def test_get_customers(self):
        """ List all customers """
        url = reverse('vapor-api:tenant-list')
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['results'][0]['name'], self.customer1.name)

    def test_create_customer(self):
        """ Post and create a customer """
        data = {
            'name': 'Test Customer 2',
            'slug': 'test-customer-2'
        }

        url = reverse('vapor-api:tenant-list')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

        custo = Customer.objects.get(pk=response.data['id'])
        self.assertEqual(custo.name, data['name'])
        self.assertEqual(custo.slug, data['slug'])


class VaporTestInterfaces(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.site1 = Site.objects.create(name='test', slug='test')
        cls.manufacturer1 = Manufacturer.objects.create(name='Vapor', slug='vapor')
        cls.devicetype1 = DeviceType.objects.create(
            model='chamber-locker',
            slug='chamber-locker',
            manufacturer=cls.manufacturer1
        )
        cls.devicerole1 = DeviceRole.objects.create(name='locker', slug='locker')
        cls.customer1 = Customer.objects.create(name='Test Customer 1', slug='test-customer-1')
        cls.device1 = Device.objects.create(
            name='network-locker',
            device_role=cls.devicerole1,
            device_type=cls.devicetype1,
            site=cls.site1,
            tenant=cls.customer1,
        )
        cls.device2 = Device.objects.create(
            name='network-locker2',
            device_role=cls.devicerole1,
            device_type=cls.devicetype1,
            site=cls.site1,
        )
        cls.interface1 = Interface.objects.create(name='e1', device=cls.device1)
        cls.interface2 = Interface.objects.create(name='xe-0/0/0', device=cls.device2)

        cls.cable = Cable(termination_a=cls.interface1, termination_b=cls.interface2)
        cls.cable.save()

    def test_get_interfaces(self):
        url = reverse('vapor-api:interface-list')
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 2)

    def test_get_customers(self):
        """ Inspect a single customers interfaces """
        base_url = reverse('vapor-api:interface-list')
        query = {'customer': self.customer1.slug}
        url = '{}?{}'.format(base_url, '&'.join(['{}={}'.format(k, v) for k, v in query.items()]))
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], self.interface1.name)
