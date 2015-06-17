from database import db_session
from models import ModelPopc

BRIDGES = []
CHANNELS = dict()
QUEUES = dict()
CALLERED = dict()

def follow_calls(msg, config):
    if msg['data'].get('EventName') \
      and msg['origin_uuid'] in config['origin_uuid']:
        data = set_channel_infos(msg)

        if data['event'] == 'CHAN_START' \
          and data['exten'] in config['extensions'] \
          and not CHANNELS.has_key(data['linkedid']):
            incoming_call(data)

        if data['event'] == 'CHAN_START' \
          and data['channel_bridge'] in BRIDGES :
            print "Via pickup call"
            answer_call(data)
    
        if data['event'] == 'BRIDGE_START' \
          and data['linkedid'] in CHANNELS \
          and data['channel'] == CHANNELS[data['linkedid']]['channel'] \
          and data['application'] == 'Queue':
            print "Via direct call"
            answer_call(data)

        if data['event'] == 'CHAN_END' \
          and (CHANNELS.has_key(data['linkedid']) \
          and data['channel'] == CHANNELS[data['linkedid']]['channel']):
            hangup_call(data)

        if data['event'] == 'APP_START' \
          and data['application'] == 'Queue' \
          and (CHANNELS.has_key(data['linkedid'])):
            what_queue(data) 

        if data['event'] == 'ANSWER' \
          and data['appdata'] == '(Outgoing Line)' \
          and "Local" not in data['channel'] \
          and data['linkedid'] != data['uniqueid'] \
          and data['linkedid'] in CHANNELS:
            print "Agent do the answer via direct call: ", data['calleridnum']
            what_callered(data)

        if data['event'] == 'BRIDGE_START' \
          and "Local" not in data['channel'] \
          and data['linkedid'] != data['uniqueid'] \
          and "Local" not in data['appdata'] \
          and data['linkedid'] in CHANNELS:
            print "Agent do the answer via pickup call: ", data['calleridnum']
            what_callered(data)

def what_callered(data):
    number = data['calleridnum']
    if not CALLERED.has_key(data['linkedid']):
        CALLERED[data['linkedid']] = number

def what_queue(data):
    queue = data['appdata'].split(',')[0]
    if data['appdata'].split(',')[7] == 'xivo_switchboard_answered_callback':
        if not QUEUES.has_key(data['linkedid']):
            QUEUES[data['linkedid']] = queue

def incoming_call(data):
    data['type'] = "incoming"
    insert_data(data)
    BRIDGES.append(data['channel'])
    CHANNELS[data['linkedid']] = dict(channel=data['channel'],
                                      calleridnum=data['calleridnum'])

    print "Incoming call"

def answer_call(data):
    if data['channel_bridge']:
        linkedid, callerid = find_linkedid_and_callerid_with_channel(data['channel_bridge'])
        data['linkedid'] = linkedid
        data['calleridnum'] = callerid
        BRIDGES.remove(data['channel_bridge'])
    data['type'] = "answer"
    if QUEUES.has_key(data['linkedid']):
        data['queue'] = QUEUES[data['linkedid']]
    insert_data(data)
    print "Call answer"

def hangup_call(data):
    data['type'] = "hangup"
    if QUEUES.has_key(data['linkedid']):
        data['queue'] = QUEUES[data['linkedid']]
        del QUEUES[data['linkedid']]
    data['calleridnum'] = data['calleridani']
    if CALLERED.has_key(data['linkedid']):
        data['callered'] = CALLERED[data['linkedid']]
        del CALLERED[data['linkedid']]
    insert_data(data)
    del CHANNELS[data['linkedid']]
    print "Call hangup"

def check_channel_bridge(channel):
    if "Bridge" in channel and not "ZOMBIE" in channel:
        return channel.split("Bridge/")[1]

    return None

def find_linkedid_and_callerid_with_channel(chan):
    for linkedid in CHANNELS:
        if CHANNELS[linkedid]['channel'] == chan:
            return (linkedid, CHANNELS[linkedid]['calleridnum'])
    return None

def set_channel_infos(msg):
    data = dict(event=msg['data']['EventName'],
                exten=set_exten(msg['data']['Exten'],msg['data']['Context']),
                time=msg['data']['EventTime'],
                linkedid=msg['data']['LinkedID'],
                uniqueid=msg['data']['UniqueID'],
                application=msg['data']['Application'],
                calleridnum=msg['data']['CallerIDnum'],
                calleridani=msg['data']['CallerIDani'],
                channel=msg['data']['Channel'],
                appdata=msg['data']['AppData'],
                channel_bridge=check_channel_bridge(msg['data']['Channel']),
                origin_uuid=msg['origin_uuid'],
                type=None
               )
    return data

def set_exten(exten, context):
    return exten + '@' + context

def insert_data(data):
    stats = ModelPopc()
    stats.callerid = data['calleridnum']
    stats.time = data['time']
    stats.type = data['type']
    stats.uniqueid = data['uniqueid']
    stats.linkedid = data['linkedid']
    stats.origin_uuid = data['origin_uuid']
    if data.has_key('queue'):
        stats.queue = data['queue']
    if data.has_key('callered'):
        stats.callered = data['callered']

    db_session.add(stats)
    db_session.commit()
