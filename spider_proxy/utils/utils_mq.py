import time
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
        credentials = pika.PlainCredentials(self.config['user'], self.config['pwd'])
        param = pika.ConnectionParameters(host=self.config['host']
                                          , port=self.config['port']
                                          , virtual_host=self.config['virtual_host']
                                          , credentials=credentials
                                          )
        return pika.BlockingConnection(param)


class Customer(object):
    def __init__(self, queueName, bindingKey, config):
        self.queueName = queueName
        self.bindingKey = bindingKey
        self.config = config
        self.connection = self._create_connection()

    def __del__(self):
        self.connection.close()

    def _create_connection(self):
        parameters = pika.ConnectionParameters(host=self.config['host']
                                          , port=self.config['port']
                                          , virtual_host=self.config['virtual_host']
                                          )
        return pika.BlockingConnection(parameters)

    def on_message_callback(self, channel, method, properties, body):
        binding_key = method.routing_key
        time.sleep(4)

        channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
        print("received new message for -" + binding_key)
        print(" [x] Received %r" % body)


    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange'],
                                 exchange_type='topic')
        channel.queue_declare(queue=self.queueName)
        channel.queue_bind(queue=self.queueName, exchange=self.config['exchange'], routing_key=self.bindingKey)
        channel.basic_consume(queue=self.queueName,
                              on_message_callback=self.on_message_callback, auto_ack=False)
        channel.basic_qos(prefetch_count=2)#, global_qos=True)
        print('[*] Waiting for data for ' + self.queueName + '. To exit press CTRL+C')
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


def get_mq_producer():

    mq_producer = Producer(PRODUCER_TOPIC, MQ_CONFIG)
        
    return mq_producer


mq_producer = get_mq_producer()

# config = {'host': '127.0.0.1',
#           'port': 5672,
#           'exchange': 'spider',
#           "virtual_host": "/spider",
#           }

# mq_customer = Customer('hello', 'topic_02', config)
# mq_customer.setup()
