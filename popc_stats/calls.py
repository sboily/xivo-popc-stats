from sqlalchemy import cast, DATE
from datetime import date
from models import CEL, POPC

BRIDGES = list()
CHANNELS = dict()
QUEUES = dict()
CALLERED = dict()

class PopcStatGenerator():

    def __init__(self, db_session, config):
        self.db_session = db_session
        self.config = config

    def follow_calls(self, msg):
        if msg['data'].get('EventName') \
          and msg['origin_uuid'] in self.config['origin_uuid']:
            data = self.set_channel_infos(msg)

            if data['event'] == 'CHAN_START' \
              and data['exten'] in self.config['extensions'] \
              and not CHANNELS.has_key(data['linkedid']):
                self.incoming_call(data)

            if data['event'] == 'CHAN_START' \
              and data['channel_bridge'] in BRIDGES :
                print "Via pickup call"
                self.answer_call(data)
    
            if data['event'] == 'BRIDGE_START' \
              and data['linkedid'] in CHANNELS \
              and data['channel'] == CHANNELS[data['linkedid']]['channel'] \
              and data['application'] == 'Queue':
                print "Via direct call"
                self.answer_call(data)

            if data['event'] == 'CHAN_END' \
              and (CHANNELS.has_key(data['linkedid']) \
              and data['channel'] == CHANNELS[data['linkedid']]['channel']):
                self.hangup_call(data)

            if data['event'] == 'APP_START' \
              and data['application'] == 'Queue' \
              and (CHANNELS.has_key(data['linkedid'])):
                self.what_queue(data) 

            if data['event'] == 'ANSWER' \
              and data['appdata'] == '(Outgoing Line)' \
              and "Local" not in data['channel'] \
              and data['linkedid'] != data['uniqueid'] \
              and data['linkedid'] in CHANNELS:
                print "Agent do the answer via direct call: ", data['calleridnum']
                self.what_callered(data)

            if data['event'] == 'BRIDGE_START' \
              and "Local" not in data['channel'] \
              and data['linkedid'] != data['uniqueid'] \
              and "Local" not in data['appdata'] \
              and data['linkedid'] in CHANNELS:
                print "Agent do the answer via pickup call: ", data['calleridnum']
                self.what_callered(data)

    def what_callered(self, data):
        number = data['calleridnum']
        if not CALLERED.has_key(data['linkedid']):
            CALLERED[data['linkedid']] = number

    def what_queue(self, data):
        queue = data['appdata'].split(',')[0]
        if data['appdata'].split(',')[7] == 'xivo_switchboard_answered_callback':
            if not QUEUES.has_key(data['linkedid']):
                QUEUES[data['linkedid']] = queue

    def incoming_call(self, data):
        data['type'] = "incoming"
        self.insert_data(data)
        BRIDGES.append(data['channel'])
        CHANNELS[data['linkedid']] = dict(channel=data['channel'],
                                          calleridnum=data['calleridnum'])

        print "Incoming call"

    def answer_call(self, data):
        if data['channel_bridge']:
            linkedid, callerid = self.find_linkedid_and_callerid_with_channel(data['channel_bridge'])
            data['linkedid'] = linkedid
            data['calleridnum'] = callerid
            BRIDGES.remove(data['channel_bridge'])
        data['type'] = "answer"
        if QUEUES.has_key(data['linkedid']):
            data['queue'] = QUEUES[data['linkedid']]
        self.insert_data(data)
        print "Call answer"

    def hangup_call(self, data):
        data['type'] = "hangup"
        if QUEUES.has_key(data['linkedid']):
            data['queue'] = QUEUES[data['linkedid']]
            del QUEUES[data['linkedid']]
        data['calleridnum'] = data['calleridani']
        if CALLERED.has_key(data['linkedid']):
            data['callered'] = CALLERED[data['linkedid']]
            del CALLERED[data['linkedid']]
        self.insert_data(data)
        del CHANNELS[data['linkedid']]
        print "Call hangup"

    def check_channel_bridge(self, channel):
        if "Bridge" in channel and not "ZOMBIE" in channel:
            return channel.split("Bridge/")[1]

        return None

    def find_linkedid_and_callerid_with_channel(self, chan):
        for linkedid in CHANNELS:
            if CHANNELS[linkedid]['channel'] == chan:
                return (linkedid, CHANNELS[linkedid]['calleridnum'])
        return None

    def set_channel_infos(self, msg):
        data = dict(event=msg['data']['EventName'],
                    exten=self.set_exten(msg['data']['Exten'],msg['data']['Context']),
                    time=msg['data']['EventTime'],
                    linkedid=msg['data']['LinkedID'],
                    uniqueid=msg['data']['UniqueID'],
                    application=msg['data']['Application'],
                    calleridnum=msg['data']['CallerIDnum'],
                    calleridani=msg['data']['CallerIDani'],
                    channel=msg['data']['Channel'],
                    appdata=msg['data']['AppData'],
                    channel_bridge=self.check_channel_bridge(msg['data']['Channel']),
                    origin_uuid=msg['origin_uuid'],
                    type=None
                   )
        return data

    def set_exten(self, exten, context):
        return exten + '@' + context

    def insert_data(self, data):
        stats = POPC()
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

        self.db_session.add(stats)

class PopcStats():
    def create_stats_from_db_popc(self):
        return self._convert_to_dict(self._get_from_db())

    def _get_from_db(self):
        return POPC.query.order_by(POPC.linkedid).all()

    def _convert_to_dict(self, data):
        calls = dict()

        for stat in data:
            if not calls.has_key(stat.linkedid):
                calls.update({stat.linkedid : { 
                               'time_incoming': '',
                               'time_answer': '',
                               'time_hangup' : '',
                               'callerid': stat.callerid,
                               'queue': '',
                               'type': 'No answer',
                               'callered': '',
                               'origin_uuid': stat.origin_uuid,
                             }})

            if stat.type == 'incoming':
                calls[stat.linkedid]['time_incoming'] = stat.time
            if stat.type == 'answer':
                calls[stat.linkedid]['time_answer'] = stat.time
                calls[stat.linkedid]['type'] = 'Answer'
            if stat.type == 'hangup':
                calls[stat.linkedid]['time_hangup'] = stat.time
            if stat.queue:
                calls[stat.linkedid]['queue'] = stat.queue
            if stat.callered:
                calls[stat.linkedid]['callered'] = stat.callered

        return self._sanit_dict(calls)

    def _sanit_dict(self, calls):
        for call in list(calls):
            if not calls[call]['queue']:
                del calls[call]
                continue
        return calls

class PopcStatConvert():
    def __init__(self, db_session, config):
        self.db_session = db_session
        self.config = config

    def insert_stats_to_db_popc(self):
        self._clean_db()
        flow = PopcStatGenerator(self.db_session, self.config)

        for row in self._get_from_db():
            data = dict(data=row.to_dict(), 
                        origin_uuid=self.config['origin_uuid'][0])
            flow.follow_calls(data)

        self.db_session.commit()

    def _get_from_db(self):
        return self.db_session.query(CEL).filter(cast(CEL.EventTime, DATE)==date.today()).order_by(CEL.EventTime)

    def _clean_db(self):
        self.db_session.query(POPC).delete()
