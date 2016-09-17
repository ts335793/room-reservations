# -*- coding: utf-8 -*

from django import forms
from django.core.exceptions import ValidationError
from room_reservations.models import FreeTerm, Room, Attribute


def hour_is_invalid_time_period_beginning(hour):
    return hour < 0 or 23 < hour


def hour_is_invalid_time_period_ending(hour):
    return hour < 1 or 24 < hour


def time_period_is_invalid(from_hour, to_hour):
    return to_hour <= from_hour


class ChooseTermForm(forms.Form):
    room_id = 0
    date = forms.DateField(label=u'Data', widget=forms.DateInput(attrs={'placeholder': 'Data w formacie dd.mm.rrrr', 'pattern': '\d{2}\.\d{2}\.\d{4}'}))
    from_hour = forms.IntegerField(label=u'Godzina rozpoczęcia', widget=forms.NumberInput(attrs={'placeholder': 'Liczba z przedziału [0, 23]', 'min': 0, 'max': 23}))
    to_hour = forms.IntegerField(label=u'Godzina zakończenia', widget=forms.NumberInput(attrs={'placeholder': 'Liczba z przedziału [1, 24]', 'min': 1, 'max': 24}))

    def __init__(self, parameters=None):
        if not (parameters is None):
            self.room_id = parameters['room_id']
        super(ChooseTermForm, self).__init__(parameters)

    def clean_from_hour(self):
        from_hour = self.cleaned_data['from_hour']
        if hour_is_invalid_time_period_beginning(from_hour):
            raise ValidationError(u'Godzina rozpoczęcia musi należeć do przedziału [0, 23].')
        return from_hour

    def clean_to_hour(self):
        to_hour = self.cleaned_data['to_hour']
        if hour_is_invalid_time_period_ending(to_hour):
            raise ValidationError(u'Godzina zakończenia musi należeć do przedziału [1, 24].')
        return to_hour

    def clean(self):
        room_id = self.room_id
        date = self.cleaned_data.get('date')
        from_hour = self.cleaned_data.get('from_hour')
        to_hour = self.cleaned_data.get('to_hour')

        if room_id is None or date is None or from_hour is None or to_hour is None:
            raise ValidationError(u'Wprowadź wszystkie dane.')

        if time_period_is_invalid(from_hour, to_hour):
            raise ValidationError(u'Przedział czasu musi się zaczynacz przed swoim końcem.')
        if FreeTerm.objects.filter(room__id=self.room_id,
                                   date=date,
                                   from_hour__lte=from_hour,
                                   to_hour__gte=to_hour).count() == 0:
            raise ValidationError(u'Wybrany termin jest niedostępny.')
        return self.cleaned_data


class ConfirmDataForm(forms.Form):
    room_id = 0
    room_name = forms.CharField(label=u'Nazwa pokoju', widget=forms.TextInput(attrs={'disabled': ''}))
    room_capacity = forms.CharField(label=u'Pojemność pokoju', widget=forms.TextInput(attrs={'disabled': ''}))
    room_description = forms.CharField(label=u'Opis pokoju', widget=forms.Textarea(attrs={'disabled': ''}))
    date = forms.DateField(label=u'Data', widget=forms.TextInput(attrs={'disabled': ''}))
    from_hour = forms.IntegerField(label=u'Godzina rozpoczęcia', widget=forms.TextInput(attrs={'disabled': ''}))
    to_hour = forms.IntegerField(label=u'Godzina zakończenia', widget=forms.TextInput(attrs={'disabled': ''}))

    def __init__(self, parameters):
        if not (parameters is None):
            self.room_id = parameters['room_id']
            room = Room.objects.get(id=self.room_id)
            parameters['room_name'] = room.name
            parameters['room_capacity'] = room.capacity
            parameters['room_description'] = room.description
        super(ConfirmDataForm, self).__init__(parameters)

    def clean_from_hour(self):
        from_hour = self.cleaned_data['from_hour']
        if hour_is_invalid_time_period_beginning(from_hour):
            raise ValidationError(u'Godzina rozpoczęcia musi należeć do przedziału [0, 23].')
        return from_hour

    def clean_to_hour(self):
        to_hour = self.cleaned_data['to_hour']
        if hour_is_invalid_time_period_ending(to_hour):
            raise ValidationError(u'Godzina zakończenia musi należeć do przedziału [1, 24].')
        return to_hour

    def clean(self):
        room_id = self.room_id
        date = self.cleaned_data.get('date')
        from_hour = self.cleaned_data.get('from_hour')
        to_hour = self.cleaned_data.get('to_hour')

        if room_id is None or date is None or from_hour is None or to_hour is None:
            raise ValidationError(u'Wprowadź wszystkie dane.')

        if time_period_is_invalid(from_hour, to_hour):
            raise ValidationError(u'Przedział czasu musi się zaczynacz przed swoim końcem.')
        if FreeTerm.objects.filter(room__id=self.room_id,
                                   date=date,
                                   from_hour__lte=from_hour,
                                   to_hour__gte=to_hour).count() == 0:
            raise ValidationError(u'Wybrany termin jest niedostępny.')
        return self.cleaned_data


class LoginForm(forms.Form):
    login = forms.CharField(label=u'Login')
    password = forms.CharField(label=u'Hasło', widget=forms.PasswordInput())


class SearchForm(forms.Form):
    search_query = forms.CharField(label=u'Zapytanie', required=False)
    attributes = forms.MultipleChoiceField(
        label=u'Atrybuty',
        required=False,
        choices=map(lambda x: (str(x), str(x)), Attribute.objects.all()))
    min_capacity = forms.IntegerField(label=u'Pojemność od', required=False, min_value=1)
    max_capacity = forms.IntegerField(label=u'Pojemność do', required=False, min_value=1)