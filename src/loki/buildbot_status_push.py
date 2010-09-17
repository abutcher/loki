# -*- test-case-name: buildbot.broken_test.runs.test_status_push -*-

"""Push events to an abstract receiver.

Implements the HTTP receiver."""

import datetime
import logging
import os
import urllib
import urlparse

try:
    import simplejson as json
except ImportError:
    import json

from buildbot.status.base import StatusReceiverMultiService
from twisted.internet import defer, reactor
from twisted.python import log
from twisted.web import client

from django.core.management import setup_environ



class LokiStatusPush(StatusReceiverMultiService):
    """Event streamer to a abstract channel.

    It uses IQueue to batch push requests and queue the data when
    the receiver is down.
    When a PersistentQueue object is used, the items are saved to disk on master
    shutdown so they can be pushed back when the master is restarted.
    """

    def __init__(self, settings_mod, queue=None, path=None, filter=True,
                 bufferDelay=1, retryDelay=5, blackList=None):
        """
        @filter: when True (default), removes all "", None, False, [] or {}
        entries.
        @bufferDelay: amount of time events are queued before sending, to
        reduce the number of push requests rate. This is the delay between the
        end of a request to initializing a new one.
        @retryDelay: amount of time between retries when no items were pushed on
        last serverPushCb call.
        @blackList: events that shouldn't be sent.
        """
        setup_environ(settings_mod)
        from django.core.cache import cache

        StatusReceiverMultiService.__init__(self)

        # Parameters.
        self.cache = cache
        self.filter = filter
        self.bufferDelay = bufferDelay
        self.retryDelay = retryDelay
        self.blackList = blackList

        # Other defaults.
        # IDelayedCall object that represents the next queued push.
        self.task = None
        self.stopped = False
        self.lastIndex = -1
        self.state = {}
        self.state['started'] = str(datetime.datetime.utcnow())
        self.state['next_id'] = 1
        self.state['last_id_pushed'] = 0

    def setServiceParent(self, parent):
        """Starting up."""
        StatusReceiverMultiService.setServiceParent(self, parent)
        self.status = self.parent.getStatus()
        self.status.subscribe(self)
        self.initialPush()

    def stopService(self):
        """Shutting down."""
        self.finalPush()
        self.stopped = True

        # Make sure all Deferreds are called on time and in a sane order.
        defers = filter(None, [d, StatusReceiverMultiService.stopService(self)])
        return defer.DeferredList(defers)

    def push(self, event, **objs):
        """Push a new event.

        """
        print event
        if self.blackList and event in self.blackList:
            return
        id = self.state['next_id']
        self.state['next_id'] += 1
        timestamp = datetime.datetime.utcnow()
        master = self.status.getProjectName()
        #packet['started'] = self.state['started']
        #event
        payload = {}


        print objs
        if 'builder' in objs and 'builderName' in objs:
            builder_name = objs['builder'].getName()
            builder_state = objs['builder'].getState()[0]
            self.cache_state('builder', builder_name, builder_state)
        elif 'builderName' in objs and 'state' in objs:
            builder_name = objs['builderName']
            builder_state = objs['state']
            self.cache_state('builder', builder_name, builder_state)

        if 'status' in objs:
            for s in objs['status'].getSlaveNames():
                s = objs['status'].getSlave(s)
                slave_name = s.getName()
                if s.isConnected():
                    slave_state = 'Connected'
                else:
                    slave_state = 'Disconnected'
                self.cache_state('slave', slave_name, slave_state)
            

    def cache_state(self, type, key, value):
        print 'setting state'
        print type, key, value

        master = self.status.getProjectName()
        key = '%s-%s-%s' % (master, type, key)
        self.cache.set(key, value, 31536000)

    #### Events

    def initialPush(self):
        # Push everything we want to push from the initial configuration.
        self.push('start', status=self.status)

    def finalPush(self):
        self.push('shutdown', status=self.status)

    def requestSubmitted(self, request):
        self.push('requestSubmitted', request=request)

    def requestCancelled(self, builder, request):
        self.push('requestCancelled', builder=builder, request=request)

    def buildsetSubmitted(self, buildset):
        self.push('buildsetSubmitted', buildset=buildset)

    def builderAdded(self, builderName, builder):
        self.push('builderAdded', builderName=builderName, builder=builder)
        return self

    def builderChangedState(self, builderName, state):
        self.push('builderChangedState', builderName=builderName, state=state)

    def buildStarted(self, builderName, build):
        self.push('buildStarted', build=build)
        return self

    def buildETAUpdate(self, build, ETA):
        self.push('buildETAUpdate', build=build, ETA=ETA)

    def stepStarted(self, build, step):
        self.push('stepStarted',
                  properties=build.getProperties().asList(),
                  step=step)

    def stepTextChanged(self, build, step, text):
        self.push('stepTextChanged',
                  properties=build.getProperties().asList(),
                  step=step,
                  text=text)

    def stepText2Changed(self, build, step, text2):
        self.push('stepText2Changed',
                  properties=build.getProperties().asList(),
                  step=step,
                  text2=text2)

    def stepETAUpdate(self, build, step, ETA, expectations):
        self.push('stepETAUpdate',
                  properties=build.getProperties().asList(),
                  step=step,
                  ETA=ETA,
                  expectations=expectations)

    def logStarted(self, build, step, log):
        self.push('logStarted',
                  properties=build.getProperties().asList(),
                  step=step)

    def logFinished(self, build, step, log):
        self.push('logFinished',
                  properties=build.getProperties().asList(),
                  step=step)

    def stepFinished(self, build, step, results):
        self.push('stepFinished',
                  properties=build.getProperties().asList(),
                  step=step)

    def buildFinished(self, builderName, build, results):
        self.push('buildFinished', build=build)

    def builderRemoved(self, builderName):
        self.push('buildedRemoved', builderName=builderName)

    def changeAdded(self, change):
        self.push('changeAdded', change=change)

    def slaveConnected(self, slavename):
        self.push('slaveConnected', slave=self.status.getSlave(slavename))

    def slaveDisconnected(self, slavename):
        self.push('slaveDisconnected', slavename=slavename)

# vim: set ts=4 sts=4 sw=4 et:
