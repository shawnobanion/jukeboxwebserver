from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^event/list/$', 'web.jukebox.views.get_events'),
                       (r'^event/create/$', 'web.jukebox.views.create_event'),
                       (r'^event/songs/(?P<event_id>[^/]+)/$', 'web.jukebox.views.get_event_songs'),
                       (r'^event/queue/(?P<event_id>[^/]+)/$', 'web.jukebox.views.get_event_queue'),
                       (r'^event/enqueuesong/(?P<event_id>[^/]+)/(?P<song_id>[^/]+)/$', 'web.jukebox.views.enqueue_song')
)
