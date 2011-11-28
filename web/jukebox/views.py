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
    try:
        event = get_event_col(is_test(request)).find_one( { '_id' : objectid.ObjectId(event_id) } )
        if 'queue' in event and any(event['queue']):
            
            queue = event['queue']
            
            # Sort the queue if bidding is enabled
            if 'bidding' in event and event['bidding'] == 'bid':
                sort_queue(queue)
                
            # Pop the first song from the list
            song = event['queue'].pop(0)
            event['queue'] = queue
            
            # Increment balance
            if any(event['queue']):
                # Whatever is smaller - the next highest bid + $1, or my maximum bid
                charged_amount = min([event['queue'][0]['bid_amount'] + 1, song['bid_amount']])
            else:
                charged_amount = song['bid_amount']
            
            if 'balance' in event:
                event['balance'] += charged_amount
            else:
                event['balance'] = charged_amount
                
            song['charged_amount'] = charged_amount
                
            # Save event
            get_event_col(is_test(request)).save(event)
            
            return HttpResponse(json.dumps(dict([(key, str(value)) for key, value in song.iteritems()])), mimetype="application/json")
            
        return HttpResponse(json.dumps(None), mimetype="application/json")
        
    except Exception as detail:
        return return_error(detail)

def get_event_balance(request, event_id):
    try:
        event = get_event_col(is_test(request)).find_one({ '_id' : objectid.ObjectId(event_id) })
        return HttpResponse(json.dumps(event['balance'] if 'balance' in event else 0), mimetype="application/json")
    except:
        raise Http404

def enqueue_song(request, event_id, song_id, user_id, bid_amount):
    try:
        get_event_col(is_test(request)).update( { '_id' : objectid.ObjectId(event_id) }, { '$push' : { 'queue' : { 'song_id' : song_id, 'user_id' : user_id, 'bid_amount' : int(bid_amount), 'timestamp' : time.time() } } } )    
        return HttpResponse('Success!')
    except Exception as detail:
        return return_error(detail)
    
def get_event_queue(request, event_id):
    try:

        event = get_event_col(is_test(request)).find_one({ '_id' : objectid.ObjectId(event_id) })
        
        if 'queue' in event:
            queue = event['queue']
            
            # Sort the queue if bidding is enabled
            if 'bidding' in event and event['bidding'] == 'bid':
                sort_queue(queue)
                
            return HttpResponse(json.dumps(queue), mimetype="application/json")
            
        return HttpResponse(json.dumps([]), mimetype="application/json")
        
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

def delete_event(request, event_id):
    try:
        event = get_event_col(is_test(request)).remove({ '_id' : objectid.ObjectId(event_id) })
        return HttpResponse('Success!')
    except:
        raise Http404

def get_events(request):
    #try:
        events = [{ 'id' : str(event['_id']), 'bidding' : event['bidding'] ,'name' : event['name'] if 'name' in event else '' } for event in get_event_col(is_test(request)).find()]
        return HttpResponse(json.dumps(events), mimetype="application/json")
#except:
#       raise Http404
    
def is_test(request):
    return 'test' in request.GET and request.GET['test'].lower() == 'true'
                            
def get_event_col(test):
    if test:
        return _db.eventsTest
    return _db.events

def return_error(detail):
    return HttpResponse('{"type":"'+str(type(detail))+'"}', mimetype="application/json")
    
def sort_queue(queue):
    queue.sort(key=lambda x: x['timestamp'])
    queue.sort(key=lambda x: x['bid_amount'], reverse=True)
