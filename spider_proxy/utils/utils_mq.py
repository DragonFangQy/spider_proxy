
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
                                 , exchange_type='topic'
                                 , durable=True)
        channel.basic_publish(exchange=self.config['exchange']
                              , routing_key=routing_key, body=message)


    def create_connection(self):
        credentials = pika.PlainCredentials(self.config['user'], self.config['pwd'])
        param = pika.ConnectionParameters(host=self.config['host']
                                          , port=self.config['port']
                                          , virtual_host=self.config['virtual_host']
                                          , credentials=credentials
                                          )
        return pika.BlockingConnection(param)


class Customer(object):
    def __init__(self, queueName, bindingKey, config, on_message_callback, prefetch_count=20):
        self.queueName = queueName
        self.bindingKey = bindingKey
        self.config = config
        self.prefetch_count = prefetch_count
        self.on_message_callback = on_message_callback
        self.connection = self._create_connection()

    def __del__(self):
        self.connection.close()

    def _create_connection(self):

        credentials = pika.PlainCredentials(self.config['user'], self.config['pwd'])
        parameters = pika.ConnectionParameters(host=self.config['host']
                                          , port=self.config['port']
                                          , virtual_host=self.config['virtual_host']
                                          , credentials=credentials
                                          , heartbeat = 120
                                          )
        return pika.BlockingConnection(parameters)

    # def on_message_callback(self, channel, method, properties, body):
    #     binding_key = method.routing_key

    #     channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
    #     print("received new message for -" + binding_key)
    #     print(" [x] Received %r" % body.decode("utf-8"))
    #     body_str = body.decode("utf-8")
    #     data_dict = json.loads(body_str)


    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange'],
                                 exchange_type='topic', 
                                 durable=True)
        channel.queue_declare(queue=self.queueName)
        channel.queue_bind(queue=self.queueName, exchange=self.config['exchange'], routing_key=self.bindingKey)
        channel.basic_consume(queue=self.queueName,
                              on_message_callback=self.on_message_callback, auto_ack=False)
        channel.basic_qos(prefetch_count=self.prefetch_count, global_qos=True)
        channel.start_consuming()

def get_mq_producer():

    mq_producer = Producer(PRODUCER_TOPIC, MQ_CONFIG)
        
    return mq_producer


mq_producer = get_mq_producer()

def get_mq_customer(queue_name, on_message_callback, prefetch_count):
    return Customer(queue_name, PRODUCER_TOPIC, MQ_CONFIG, on_message_callback, prefetch_count)
