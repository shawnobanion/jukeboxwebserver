from django.http import HttpResponse, Http404
import json
import time
#import operator
from pymongo import Connection, objectid,ASCENDING, DESCENDING
from django.views.decorators.csrf import csrf_exempt

_con = Connection('jukebox-shawnobanion-db-0.dotcloud.com', 13105)
_db = _con['admin']
_db.authenticate('root', 'as1sVjw5IgIzfii9Rhsi')

def clean(request):
    try:
        get_event_col(is_test(request)).drop()
        return HttpResponse('All clean.')
    except:
        raise Http404

def get_event_songs(request, event_id):
    try:
        event = get_event_col(is_test(request)).find_one({ '_id' : objectid.ObjectId(event_id) })
        return HttpResponse(json.dumps(event['songs']), mimetype="application/json")
    except:
        raise Http404

def dequeue_song(request, event_id):
    #song = get_event_col(is_test(request)).update( { '_id' : objectid.ObjectId(event_id) }, { '$pop' : { 'queue' : -1 } } )
    try:
        event = get_event_col(is_test(request)).find_one( { '_id' : objectid.ObjectId(event_id) } )
        if 'queue' in event and any(event['queue']):
            song = event['queue'].pop(0)
            get_event_col(is_test(request)).save(event)
            return HttpResponse(json.dumps(dict([(key, str(value)) for key, value in song.iteritems()])), mimetype="application/json")
        return HttpResponse(json.dumps(None), mimetype="application/json")
    except Exception as detail:
        return return_error(detail)

def enqueue_song(request, event_id, song_id, user_id, bid_amount):
    try:
        get_event_col(is_test(request)).update( { '_id' : objectid.ObjectId(event_id) }, { '$push' : { 'queue' : { 'song_id' : song_id, 'user_id' : user_id, 'bid_amount' : bid_amount, 'timestamp' : time.time() } } } )    
        return HttpResponse('Success!')
    except Exception as detail:
        return return_error(detail)
    
def get_event_queue(request, event_id):
    try:
        event = get_event_col(is_test(request)).find_one({ '_id' : objectid.ObjectId(event_id) })
        
        if 'queue' in event:
            queue = event['queue']
            queue.sort(key=lambda x: x['timestamp'])
            queue.sort(key=lambda x: x['bid_amount'], reverse=True)
            return HttpResponse(json.dumps(queue), mimetype="application/json")
            
        return HttpResponse(json.dumps([]), mimetype="application/json")
        
        #return HttpResponse(json.dumps(sorted(event['queue'], key=lambda x: x['bid_amount'], reverse=True) if 'queue' in event else []), mimetype="application/json")
        
    except:
        raise Http404

@csrf_exempt
def create_event(request):
    try:
        if request.method == 'POST':
            event = json.loads(request.raw_post_data)
            get_event_col(is_test(request)).save(event)
            return HttpResponse(event['_id'])
        return HttpResponse('Event was not added.')
    except:
        raise Http404

def get_events(request):
    #try:
        events = [{ 'id' : str(event['_id']), 'bidding' : event['bidding'] ,'name' : event['name'] if 'name' in event else '' } for event in get_event_col(is_test(request)).find()]
        return HttpResponse(json.dumps(events), mimetype="application/json")
#except:
#       raise Http404
    
def is_test(request):
    #if request.method == 'POST':
    #    return 'test' in request.POST and request.POST['test'].lower() == 'true'
    #else:
        return 'test' in request.GET and request.GET['test'].lower() == 'true'
                            
def get_event_col(test):
    if test:
        return _db.eventsTest
    return _db.events

def return_error(detail):
    return HttpResponse('{"type":"'+str(type(detail))+'"}', mimetype="application/json")