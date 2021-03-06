#!/usr/bin/env python3


import asyncio
import time
import json
import uuid
import datetime
import sys

from bootstrapper_subscriber import Subscriber
from bootstrapper_publisher import Publisher
from bootstrapper_harness import Harness
from bootstrapper_driver import BootstrapperDriver

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner 

loop = asyncio.get_event_loop()




def make_connection():
    if loop.is_running():
        loop.stop()
    coro = loop.create_connection(transport_factory, '0.0.0.0', 8080)
    transport, protocoler = loop.run_until_complete(coro)
    #protocoler.set_outer(self)
    if not loop.is_running():
        loop.run_forever()


class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """
    outer = None

    def set_outer(self, outer_):
        outer = outer_

    def onConnect(self):
        """Callback fired when the transport this session will run over has been established.
        """
        self.join(u"ot_realm")


    @asyncio.coroutine
    def onJoin(self, details):
        """Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        Starts instatiation of robot objects by calling :meth:`otone_client.instantiate_objects`.
        """
        print(datetime.datetime.now(),' - driver_client : WampComponent.onJoin:')
        print('\targs:',locals())
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
    
        #def handshake(client_data):
        #    """
        #    """
        #    #if debug == True:
        #    print(datetime.datetime.now(),' - driver_client : WampComponent.handshake:')
        #    #if outer is not None:
        #    #outer.
        #    publisher.handshake(client_data)

        #yield from self.subscribe(handshake, 'com.opentrons.driver_handshake')
        yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.bootstrapper')



    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        print('driver_client : WampComponent.onLeave:')
        print('\targs:',locals())
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            raise
        

    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        print(datetime.datetime.now(),' - bootstrapper_client : WampComponent.onDisconnect')
        asyncio.get_event_loop().stop()

    
    


if __name__ == '__main__':

    try:
        session_factory = wamp.ApplicationSessionFactory()
        session_factory.session = WampComponent
        session_factory._myAppSession = None

        url = "ws://0.0.0.0:8080/ws"
        transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                                url=url,
                                                                debug=False,
                                                                debug_wamp=False)
        loop = asyncio.get_event_loop()

        # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
        # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
        print('*\t*\t* initial setup - publisher, harness, subscriber\t*\t*\t*')
        publisher = Publisher(session_factory)
        bootstrapper_harness = Harness(publisher)
        subscriber = Subscriber(bootstrapper_harness,publisher)
        bootstrapper_harness.set_publisher(publisher)


        # INSTANTIATE DRIVERS:
        print('*\t*\t* instantiate drivers\t*\t*\t*')
        bootie_driver = BootstrapperDriver()


        # ADD DRIVERS TO HARNESS 
        print('*\t*\t* add drivers to harness\t*\t*\t*')   
        bootstrapper_harness.add_driver('frontend','bootstrapper',bootie_driver)
        print(bootstrapper_harness.drivers(publisher.id,None,None))

        # DEFINE CALLBACKS:
        #
        #   data_dict format:
        #
        #
        #
        #
        #
        print('*\t*\t* define callbacks\t*\t*\t*')
        def bootstrapper(name, data_dict):
            """
            """
            print(datetime.datetime.now(),' - bootstrapper_client.bootstrapper')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('frontend','','bootstrapper',name,dd_name,dd_value)

        #def none(name, data_dict):
        #    """
        #    """
        #    print(datetime.datetime.now(),' - driver_client.none:')
        #    print('\tdata_dict: ',data_dict)
        #    dd_name = list(data_dict)[0]
        #    dd_value = data_dict[dd_name]
        #    publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)

        #def positions(name, data_dict):
        #    """
        #    """
        #    print(datetime.datetime.now(),' - driver_client.positions:')
        #    print('\tdata_dict: ',data_dict)
        #    dd_name = list(data_dict)[0]
        #    dd_value = data_dict[dd_name]
        #    publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)


        # ADD CALLBACKS VIA HARNESS:
        print('*\t*\t* add callbacks via harness\t*\t*\t*')
        bootstrapper_harness.add_callback(publisher.id,'bootstrapper', {bootstrapper:['None']})
        #driver_harness.add_callback(publisher.id,'smoothie', {positions:['M114']})

        #show what was added
        for d in bootstrapper_harness.drivers(publisher.id,None,None):
            print(bootstrapper_harness.callbacks(publisher.id,d, None))

        # CONNECT TO DRIVERS:
        print('*\t*\t* connect to drivers\t*\t*\t*')
        #driver_harness.connect(publisher.id,'smoothie',None)

        print('END INIT')

        make_connection()

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()














