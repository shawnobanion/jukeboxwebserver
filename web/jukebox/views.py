from django.http import HttpResponse
import json
from pymongo import Connection, objectid
from django.views.decorators.csrf import csrf_exempt

_con = Connection('jukebox-shawnobanion-db-0.dotcloud.com', 13105)
_db = _con['admin']
_db.authenticate('root', 'as1sVjw5IgIzfii9Rhsi')

def get_event_songs(request, event_id):
    event = _db.events.find_one({ '_id' : objectid.ObjectId(event_id) })
    return HttpResponse(json.dumps(event['songs']), mimetype="application/json")

def enqueue_song(request, event_id, song_id):
    _db.events.update( { '_id' : objectid.ObjectId(event_id) }, { '$push' : { 'queue' : song_id } } )    
    return HttpResponse('Success!')
    
def get_event_queue(request, event_id):
    event = _db.events.find_one({ '_id' : objectid.ObjectId(event_id) })
    return HttpResponse(json.dumps(event['queue'] if 'queue' in event else ''), mimetype="application/json")

@csrf_exempt
def create_event(request):
    """
    Creates an event.
    """
    if request.method == 'POST':
        event = json.loads(request.raw_post_data)
        _db.events.save(event)
        return HttpResponse(event['_id'])
    return HttpResponse('Event was not added.')
    return None

def get_events(request):
    events = [{ 'id' : str(event['_id']), 'name' : event['name'] } for event in _db.events.find()]
    return HttpResponse(json.dumps(events), mimetype="application/json")