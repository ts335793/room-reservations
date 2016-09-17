from django.test import TestCase
from room_reservations.models import Room, FreeTerm, Reservation
from django.core.exceptions import ValidationError
from django.contrib import auth
from django.test import Client
from django.core.urlresolvers import reverse
import pprint


class LoginPermissionsTestCase(TestCase):
    def test_choose_term(self):
        '''
        Test if might access choose term page when being logged out.
        '''
        client = Client()
        response = client.get(reverse('choose_term', kwargs={'room_id': 10}))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('choose_term', kwargs={'room_id': 10}))

    def test_confirm_data(self):
        '''
        Test if might access confirm data page when being logged out.
        '''
        client = Client()
        response = client.get(reverse('confirm_data', kwargs={'room_id': 1, 'date': '2014-04-24', 'from_hour': 1, 'to_hour': 5}))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('confirm_data', kwargs={'room_id': 1, 'date': '2014-04-24', 'from_hour': 1, 'to_hour': 5}))

    def test_choose_room(self):
        '''
        Test if might access choose room page when being logged out.
        '''
        client = Client()
        response = client.get(reverse('choose_room'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('choose_room'))


class RoomTestCase(TestCase):
    def test_no_name(self):
        room = Room(capacity=100, description='...')
        try:
            room.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_no_capacity(self):
        room = Room(name='aaa', description='asdf')
        try:
            room.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_no_description(self):
        room = Room(name='aaas', capacity=2)
        try:
            room.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)


class FreeTermTestCase(TestCase):
    def setUp(self):
        self.room = Room(name='room', capacity=10, description='...')
        self.date = '2014-05-16'

        self.room.save()

        free_term = FreeTerm(room=self.room, date='2014-05-16', from_hour=10, to_hour=15)
        free_term.save()

        auth.models.User.objects.create_user('panjan', '', 'pass')
        user = auth.models.User.objects.get(username='panjan')

        reservation = Reservation(room=self.room, date='2014-05-16', from_hour=4, to_hour=6, user=user)
        reservation.save()

    def test_overlap_1(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=0, to_hour=5)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_2(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=5, to_hour=6)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_3(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=5, to_hour=10)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_4(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=7, to_hour=12)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_5(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=5, to_hour=10)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_6(self):
        tf = FreeTerm(room=self.room, date='2014-05-16', from_hour=0, to_hour=9)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

class ReservationTestCase(TestCase):
    def setUp(self):
        self.room = Room(name='room', capacity=10, description='...')
        self.date = '2014-05-16'

        self.room.save()

        free_term = FreeTerm(room=self.room, date='2014-05-16', from_hour=10, to_hour=15)
        free_term.save()

        auth.models.User.objects.create_user('panjan', '', 'pass')
        self.user = auth.models.User.objects.get(username='panjan')

        reservation = Reservation(room=self.room, date='2014-05-16', from_hour=4, to_hour=6, user=self.user)
        reservation.save()

    def test_overlap_1(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=0, to_hour=5, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_2(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=5, to_hour=6, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_3(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=5, to_hour=10, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_4(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=7, to_hour=12, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_5(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=5, to_hour=10, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)

    def test_overlap_6(self):
        tf = Reservation(room=self.room, date='2014-05-16', from_hour=0, to_hour=9, user=self.user)
        try:
            tf.save()
        except ValidationError:
            pass
        else:
            self.assertTrue(False)


class ReservationNoBoundsTestCase(TestCase):
    def setUp(self):
        auth.models.User.objects.create_user('mikolaj', '', 'hohoho')

        self.user = auth.models.User.objects.get(username='mikolaj')
        self.client = Client()
        self.client.post(reverse('log_in'), {'login': 'mikolaj', 'password': 'hohoho'})

        self.room = Room(name='sdgf', capacity=123, description='21321213')
        self.room.save()

    def test(self):
        ft = FreeTerm(room=self.room, date='2014-11-27', from_hour=10, to_hour=14)
        ft.save()

        self.client.post(reverse('confirm_data', kwargs={'room_id': self.room.id, 'date': '2014-11-27', 'from_hour': 10, 'to_hour': 14}), {'asdasdas': 'qwe'}, follow=True)
        self.assertEquals(FreeTerm.objects.all().count(), 0)
        self.assertEquals(Reservation.objects.all().count(), 1)
        self.assertEquals(Reservation.objects.filter(room=self.room, user=self.user, date='2014-11-27', from_hour=10, to_hour=14).count(), 1)


class ReservationLowerBoundTestCase(TestCase):
    def setUp(self):
        auth.models.User.objects.create_user('mikolaj', '', 'hohoho')

        self.user = auth.models.User.objects.get(username='mikolaj')
        self.client = Client()
        self.client.post(reverse('log_in'), {'login': 'mikolaj', 'password': 'hohoho'})

        self.room = Room(name='sdgf', capacity=123, description='21321213')
        self.room.save()

    def test(self):
        ft = FreeTerm(room=self.room, date='2014-11-27', from_hour=9, to_hour=14)
        ft.save()

        self.client.post(reverse('confirm_data', kwargs={'room_id': self.room.id, 'date': '2014-11-27', 'from_hour': 10, 'to_hour': 14}), {'asdasdas': 'qwe'}, follow=True)
        self.assertEquals(FreeTerm.objects.all().count(), 1)
        self.assertEquals(FreeTerm.objects.filter(room=self.room, date='2014-11-27', from_hour=9, to_hour=10).count(), 1)
        self.assertEquals(Reservation.objects.all().count(), 1)
        self.assertEquals(Reservation.objects.filter(room=self.room, user=self.user, date='2014-11-27', from_hour=10, to_hour=14).count(), 1)


class ReservationUpperBoundTestCase(TestCase):
    def setUp(self):
        auth.models.User.objects.create_user('mikolaj', '', 'hohoho')

        self.user = auth.models.User.objects.get(username='mikolaj')
        self.client = Client()
        self.client.post(reverse('log_in'), {'login': 'mikolaj', 'password': 'hohoho'})

        self.room = Room(name='sdgf', capacity=123, description='21321213')
        self.room.save()

    def test(self):
        ft = FreeTerm(room=self.room, date='2014-11-27', from_hour=10, to_hour=16)
        ft.save()

        self.client.post(reverse('confirm_data', kwargs={'room_id': self.room.id, 'date': '2014-11-27', 'from_hour': 10, 'to_hour': 14}), {'asdasdas': 'qwe'}, follow=True)
        self.assertEquals(FreeTerm.objects.all().count(), 1)
        self.assertEquals(FreeTerm.objects.filter(room=self.room, date='2014-11-27', from_hour=14, to_hour=16).count(), 1)
        self.assertEquals(Reservation.objects.all().count(), 1)
        self.assertEquals(Reservation.objects.filter(room=self.room, user=self.user, date='2014-11-27', from_hour=10, to_hour=14).count(), 1)


class ReservationBothBoundsTestCase(TestCase):
    def setUp(self):
        auth.models.User.objects.create_user('mikolaj', '', 'hohoho')

        self.user = auth.models.User.objects.get(username='mikolaj')
        self.client = Client()
        self.client.post(reverse('log_in'), {'login': 'mikolaj', 'password': 'hohoho'})

        self.room = Room(name='sdgf', capacity=123, description='21321213')
        self.room.save()

    def test(self):
        ft = FreeTerm(room=self.room, date='2014-11-27', from_hour=7, to_hour=16)
        ft.save()

        self.client.post(reverse('confirm_data', kwargs={'room_id': self.room.id, 'date': '2014-11-27', 'from_hour': 10, 'to_hour': 14}), {'asdasdas': 'qwe'}, follow=True)
        self.assertEquals(FreeTerm.objects.all().count(), 2)
        self.assertEquals(FreeTerm.objects.filter(room=self.room, date='2014-11-27', from_hour=7, to_hour=10).count(), 1)
        self.assertEquals(FreeTerm.objects.filter(room=self.room, date='2014-11-27', from_hour=14, to_hour=16).count(), 1)
        self.assertEquals(Reservation.objects.all().count(), 1)
        self.assertEquals(Reservation.objects.filter(room=self.room, user=self.user, date='2014-11-27', from_hour=10, to_hour=14).count(), 1)