from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='main.html'), name='main'),
    url(r'^log_in/$', 'room_reservations.views.log_in', name='log_in'),
    url(r'^create_account/$', 'room_reservations.views.create_account', name='create_account'),
    url(r'^log_out/$', 'room_reservations.views.log_out', name='log_out'),
    url(r'^choose_room/$', 'room_reservations.views.choose_room', name='choose_room'),
    url(r'^choose_term/room/(?P<room_id>\d+)/$', 'room_reservations.views.choose_term', name='choose_term'),
    url(r'^confirm_data/room/(?P<room_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/from_hour/(?P<from_hour>\d+)/'
        r'to_hour/(?P<to_hour>\d+)/', 'room_reservations.views.confirm_data', name='confirm_data'),
    url(r'^get_free_terms/room/(?P<room_id>\d+)/', 'room_reservations.views.get_free_terms', name='get_free_terms'),
)
