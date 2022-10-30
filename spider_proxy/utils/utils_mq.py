import pika

from spider_proxy.spider_common.config import PRODUCER_TOPIC,MQ_CONFIG


class Producer(object):

    def __init__(self, routing_key, config):
        self.config = config
        self.routing_key = routing_key
        self.connection = self.create_connection()

    def send_message(self, message, routing_key=None):

        if not routing_key:
            routing_key = self.routing_key
            
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange']
                                 , exchange_type='topic')
        channel.basic_publish(exchange=self.config['exchange']
                              , routing_key=routing_key, body=message)

        print("[x] Sent message %r for %r" % (message, routing_key))

    def create_connection(self):
        param = pika.ConnectionParameters(host=self.config['host']
                                          , port=self.config['port']
                                          , virtual_host=self.config['virtual_host']
                                          )
        return pika.BlockingConnection(param)


mq_producer = None

def get_mq_producer():

    global mq_producer
    
    if not mq_producer:
        mq_producer = Producer(PRODUCER_TOPIC, MQ_CONFIG)
        
    return mq_producer


