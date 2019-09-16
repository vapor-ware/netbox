from dcim.models import (
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
    def setUp(self):
        super().setUp()

        self.customer1 = Customer.objects.create(name='Test Customer 1', slug='test-customer-1')
       

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

    def setUp(self):
        super().setUp()

        self.site1 = Site.objects.create(name='test', slug='test')
        self.manufacturer1 = Manufacturer.objects.create(name='Vapor', slug='vapor')
        self.devicetype1 = DeviceType.objects.create(model='chamber-locker', slug='chamber-locker', manufacturer=self.manufacturer1)
        self.devicerole1 = DeviceRole.objects.create(name='locker', slug='locker')
        self.device1 = Device.objects.create(name='network-locker', device_role=self.devicerole1, device_type=self.devicetype1, site=self.site1)
        self.interface1 =  Interface.objects.create(name='e1', device=self.device1)

    def test_get_interfaces(self):
        url = reverse('vapor-api:interface-list')
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 1)
