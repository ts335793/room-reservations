# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import auth


def time_period_overlaps_some_time_period_in_model(period, model):
    return model.objects.filter(room=period.room, date=period.date) \
                        .filter(Q(from_hour__range=(period.from_hour, period.to_hour - 1)) |
                                Q(to_hour__range=(period.from_hour + 1, period.to_hour))).count() > 0 or \
           model.objects.filter(room=period.room, date=period.date,
                                from_hour__lte=period.from_hour, to_hour__gte=period.to_hour).count() > 0


def time_period_beginning_is_invalid(period):
    return period.from_hour < 0 or 23 < period.from_hour


def time_period_ending_is_invalid(period):
    return period.to_hour < 1 or 24 < period.to_hour


def time_period_is_invalid(period):
    return period.to_hour <= period.from_hour


class Attribute(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'nazwa', unique=True)

    def __unicode__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'nazwa')
    capacity = models.IntegerField(verbose_name=u'pojemność')
    description = models.CharField(max_length=1000, verbose_name=u'opis')
    attributes = models.ManyToManyField(Attribute, verbose_name=u'atrybuty')

    def clean(self):
        if self.capacity < 0:
            raise ValidationError(u'Pojemność pokoju musi być większa od zera.')

    def save(self):
        self.full_clean()
        super(Room, self).save()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'pokój'
        verbose_name_plural = u'pokoje'


class FreeTerm(models.Model):
    room = models.ForeignKey(Room, verbose_name=u'pokój')
    date = models.DateField(verbose_name=u'data')
    from_hour = models.IntegerField(verbose_name=u'godzina rozpoczęcia')
    to_hour = models.IntegerField(verbose_name=u'godzina zakończenia')

    def clean(self):
        if time_period_beginning_is_invalid(self):
            raise ValidationError(u'Początek terminu musi być liczbą całkowitą z przedziału [0, 23].')

        if time_period_ending_is_invalid(self):
            raise ValidationError(u'Koniec terminu musi być liczbą całkowitą z przedziału [1,24].')

        if time_period_is_invalid(self):
            raise ValidationError(u'Termin musi się zaczynać przed swoim końcem.')

        if time_period_overlaps_some_time_period_in_model(self, FreeTerm):
            raise ValidationError(u'Wolny termin nachodzi na inny wolny termin.')

        if time_period_overlaps_some_time_period_in_model(self, Reservation):
            raise ValidationError(u'Wolny termin nachodzi na rezerwację.')

    def save(self):
        FreeTerm.objects.select_for_update().all()
        Reservation.objects.select_for_update().all()
        self.full_clean()
        super(FreeTerm, self).save()

    def __unicode__(self):
        return u'Wolny termin w pokoju ' + self.room.name \
               + u' w dniu ' + str(self.date) \
               + u' w godzinach ' + str(self.from_hour) + ' - ' + str(self.to_hour)

    class Meta:
        verbose_name = u'wolny termin'
        verbose_name_plural = u'wolne terminy'


class Reservation(models.Model):
    room = models.ForeignKey(Room, verbose_name=u'pokój')
    date = models.DateField(verbose_name=u'data')
    from_hour = models.IntegerField(verbose_name=u'godzina rozpoczęcia')
    to_hour = models.IntegerField(verbose_name=u'godzina zakończenia')
    user = models.ForeignKey(auth.models.User, verbose_name=u'rezerwujący')

    def clean(self):
        if time_period_beginning_is_invalid(self):
            raise ValidationError(u'Początek terminu musi być liczbą całkowitą z przedziału [0, 23].')

        if time_period_ending_is_invalid(self):
            raise ValidationError(u'Koniec terminu musi być liczbą całkowitą z przedziału [1,24].')

        if time_period_overlaps_some_time_period_in_model(self, FreeTerm):
            raise ValidationError(u'Rezerwacja nachodzi na wolny termin.')

        if time_period_overlaps_some_time_period_in_model(self, Reservation):
            raise ValidationError(u'Rezerwacja nachodzi na inną rezerwację.')

    def save(self):
        FreeTerm.objects.select_for_update().all()
        Reservation.objects.select_for_update().all()
        self.full_clean()
        super(Reservation, self).save()

    def __unicode__(self):
        return u'Rezerwacja pokoju ' + self.room.name \
               + u' w dniu ' + str(self.date) \
               + u' w godzinach ' + str(self.from_hour) + ' - ' + str(self.to_hour) \
               + u' przez ' + str(self.user.username)

    class Meta:
        verbose_name = u'rezerwacja'
        verbose_name_plural = u'rezerwacje'