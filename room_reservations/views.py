# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from room_reservations import forms
from room_reservations.models import Room, FreeTerm, Reservation
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponse
from django.core.urlresolvers import reverse
import json
from django.template.defaultfilters import date


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('main')
            else:
                messages.info(request, u'Konto jest zablokowane.')
        else:
            messages.info(request, u'Zły login lub hasło.')
    return render(request, 'log_in.html')


def create_account(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        if auth.models.User.objects.filter(username=username).count() > 0:
            messages.info(request, u'Już istnieje użytkownik z podanym loginem.')
        else:
            auth.models.User.objects.create_user(username, '', password)
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('main')
    return render(request, 'create_account.html')


def log_out(request):
    auth.logout(request)
    return redirect('main')


@login_required
def choose_room(request):
    if request.method == 'POST':
        pass

    rooms = Room.objects.all()
    if request.GET.get('order'):
        order = request.GET.get('order')
        if order == 'name':
            rooms = rooms.order_by('name')
        if order == '-name':
            rooms = rooms.order_by('-name')
        if order == 'capacity':
            rooms = rooms.order_by('capacity')
        if order == '-capacity':
            rooms = rooms.order_by('-capacity')
    if request.GET.get('search_query'):
        search = request.GET.get('search_query')
        if search.isdigit():
            rooms = rooms.filter(Q(name__icontains=search) | Q(description__icontains=search) | Q(capacity=search))
        else:
            rooms = rooms.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if request.GET.getlist('attributes'):
        for attribute in request.GET.getlist('attributes'):
            rooms = rooms.filter(attributes__name=attribute)
    if request.GET.get('min_capacity') and request.GET.get('min_capacity').isdigit():
        rooms = rooms.filter(capacity__gte=request.GET.get('min_capacity'))
    if request.GET.get('max_capacity') and request.GET.get('max_capacity').isdigit():
        rooms = rooms.filter(capacity__lte=request.GET.get('max_capacity'))

    paginator = Paginator(rooms, 10)
    if request.GET.get('page') and request.GET.get('page').isdigit() and int(request.GET.get('page')) <= paginator.page_range[-1]:
        page = request.GET.get('page')
    else:
        page = 1

    return render(request, 'choose_room.html', {
        'rooms': paginator.page(page),
        'search_form': forms.SearchForm(request.GET),
        'attributes': request.GET.getlist('attributes'),
        'min_capacity': request.GET.get('min_capacity'),
        'max_capacity': request.GET.get('max_capacity'),
        'search_query': request.GET.get('search_query'),
        'order': request.GET.get('order'),
    })


@login_required
def choose_term(request, room_id):
    if Room.objects.filter(id=room_id).count() == 0:
        return HttpResponseNotFound(u'Nie znaleziono pokoju.')
    if request.method == 'POST':
        form = forms.ChooseTermForm({'room_id': room_id,
                                     'date': request.POST.get('date'),
                                     'from_hour': request.POST.get('from_hour'),
                                     'to_hour': request.POST.get('to_hour')})
        if form.is_valid():
            return redirect(reverse('confirm_data', kwargs={'room_id': int(room_id),
                                                            'date': str(form.cleaned_data['date']),
                                                            'from_hour': int(form.cleaned_data['from_hour']),
                                                            'to_hour': int(form.cleaned_data['to_hour'])}))
    else:
        form = forms.ChooseTermForm()
    free_terms = FreeTerm.objects.filter(room__id=room_id).order_by('date', 'from_hour')
    return render(request, 'choose_term.html', {'free_terms': free_terms, 'form': form, 'room_id': room_id})



@login_required
def confirm_data(request, room_id, date, from_hour, to_hour):
    if Room.objects.filter(id=room_id).count() == 0:
        return HttpResponseNotFound(u'Nie znaleziono pokoju.')
    form = forms.ConfirmDataForm({'room_id': room_id,
                                  'date': date,
                                  'from_hour': from_hour,
                                  'to_hour': to_hour})
    if request.method == 'POST':
        # lock database
        Room.objects.select_for_update().all()
        FreeTerm.objects.select_for_update().all()
        Reservation.objects.select_for_update().all()
        if Room.objects.filter(id=room_id).count() == 0:
            return HttpResponseNotFound(u'Nie znaleziono pokoju.')
        if form.is_valid():
            room_id = room_id
            date = form.cleaned_data['date']
            from_hour = form.cleaned_data['from_hour']
            to_hour = form.cleaned_data['to_hour']
            # free term to be deleted
            space = FreeTerm.objects.get(room_id=room_id, date=date, from_hour__lte=from_hour, to_hour__gte=to_hour)
            space.delete()
            # lower bound
            if space.from_hour < from_hour:
                lower_bound = FreeTerm(room=space.room, date=space.date, from_hour=space.from_hour, to_hour=from_hour)
                lower_bound.save()
            # upper bound
            if to_hour < space.to_hour:
                upper_bound = FreeTerm(room=space.room, date=space.date, from_hour=to_hour, to_hour=space.to_hour)
                upper_bound.save()
            # reservation
            reservation = Reservation(room=space.room, date=space.date, from_hour=from_hour, to_hour=to_hour, user=request.user)
            reservation.save()
            # redirect main page
            messages.info(request, u'Pomyślnie zarezerwowano pokój ' + form.cleaned_data['room_name'] +
                                   u' na ' + str(date) +
                                   u' w godzinach ' + str(from_hour) + ' - ' + str(to_hour) + u'.')
            return redirect('main')
        else:
            messages.info(request, u'Nie udało się zarezerwować pokoju.')
    return render(request, 'confirm_data.html', {'form': form})

@login_required
def get_free_terms(request, room_id):
    print room_id
    response_data = []
    for term in FreeTerm.objects.filter(room__id=room_id).order_by('date', 'from_hour'):
        print len(response_data) == 0
        if len(response_data) == 0 or date(term.date, 'j E Y') != response_data[-1]['display_date']:
            response_data.append({'display_date': date(term.date, 'j E Y'), 'free_terms': []})
        day = response_data[-1]
        day['free_terms'].append({'from_hour': term.from_hour, 'to_hour': term.to_hour})
        #if date(term.date, 'j E Y') not in response_data:
        #    response_data[date(term.date, 'j E Y')] = []
        #response_data[date(term.date, 'j E Y')].append({'from_hour': term.from_hour, 'to_hour': term.to_hour})
    return HttpResponse(json.dumps(response_data), content_type="application/json")