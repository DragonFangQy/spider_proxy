

import json
import sys
import logging
import time

from confluent_kafka import Producer, Consumer, KafkaException

from spider_proxy.spider_common import config
from spider_proxy.utils.utils_log import my_logger


class KafkaProducer(object):

    def __init__(self) -> None:
        self.kafka_producer = Producer(**config.KAFKA_PRODUCER_CONF, logger=my_logger)


    def delivery_callback(self, err, msg):

        if err:
            print(f"message failed delivery: {err}")
            my_logger.exception(f"message failed delivery: {err}")
        else:
            # print(f"Message delivered to topic:'{msg.topic()}' partition:'{msg.partition()}' offset:'{msg.offset()}'")
            my_logger.debug(f"Message delivered to topic:'{msg.topic()}' partition:'{msg.partition()}' offset:'{msg.offset()}'")
            div, mod = divmod(msg.offset(), config.KAFKA_LOGS_ONCE)
            if mod == 0:
                # print(f"Message delivered to topic:'{msg.topic()}' partition:'{msg.partition()}' offset:'{msg.offset()}'")
                my_logger.info(f"Message delivered to topic:'{msg.topic()}' partition:'{msg.partition()}' offset:'{msg.offset()}'")


    def send_message_single(self, message):
        
        if isinstance(message, dict): 
            message = json.dumps(message) 
        elif not isinstance(message, str):
            raise ValueError("message_list element not meet the requirement")
        self.kafka_producer.produce(config.KAFKA_TOPIC, message, callback=self.delivery_callback)
        self.kafka_producer.poll(config.KAFKA_POLL_TIMEOUT)
        self.kafka_producer.flush()


    def send_message_value(self, message_list):
        
        for message in message_list:

            if isinstance(message, dict): 
                message = json.dumps(message) 
            elif not isinstance(message, str):
                raise ValueError("message_list element not meet the requirement")
            self.kafka_producer.produce(config.KAFKA_TOPIC, message, callback=self.delivery_callback)
            self.kafka_producer.poll(config.KAFKA_POLL_TIMEOUT)

        self.kafka_producer.flush()
        

    def send_message_kv(self, message_dict):
        
        for message_key, message_value in message_dict.items():
            if not isinstance(message_key, str):
                raise ValueError(f"message_dict message_key:'{message_dict}' not meet the requirement")

            if isinstance(message_value, dict): 
                message = json.dumps(message) 
            elif not isinstance(message_value, str):
                raise ValueError("message_list element not meet the requirement")
            
            self.kafka_producer.produce(config.KAFKA_TOPIC, value=message, key=message, callback=self.delivery_callback)
            self.kafka_producer.poll(config.KAFKA_POLL_TIMEOUT)

        self.kafka_producer.flush()
 

    def _demo(self):
        
        self.kafka_producer = Producer(** { 
                    "bootstrap.servers": "192.168.43.90:9095",
                    "compression.type":"gzip", 
                }
            )
        
        for i in range(100):
            self.kafka_producer.produce("test_topic", key=f"index_i",value=f"kafka_producer index {i}", callback=self.delivery_callback)
            # self.kafka_producer.produce(config.KAFKA_TOPIC, f"kafka_producer index {i}", callback=self.delivery_callback)

            self.kafka_producer.poll(0)
        sys.stderr.write('%% Waiting for %d deliveries\n' % len(self.kafka_producer))
        self.kafka_producer.flush()




class KafkaConsumer(object):

    def __init__(self, topics, on_assign=None, on_revoke=None, on_lost=None, callback=None) -> None:
        
        self.kafka_consumer = Consumer(**config.KAFKA_CONSUMER_CONF, logger=my_logger)
        
        subscribe_info = self.get_subscribe_info(on_assign=on_assign, on_revoke=on_revoke, on_lost=on_lost) 
        self.kafka_consumer.subscribe(topics, **subscribe_info)
        self.run_status = True
        self.callback = callback
        if callback:
            self._consume_message()

    def get_subscribe_info(self, on_assign=None, on_revoke=None, on_lost=None):
        temp_dict = {}
        if on_assign:
            temp_dict.update({"on_assign": on_assign})
        if on_revoke:
            temp_dict.update({"on_revoke": on_revoke})
        if on_lost:
            temp_dict.update({"on_lost": on_lost})

        return temp_dict


    def set_subscribe(self, topics, on_assign=None, on_revoke=None, on_lost=None):
        subscribe_info = self.get_subscribe_info(on_assign=on_assign, on_revoke=on_revoke, on_lost=on_lost) 
        self.kafka_consumer.subscribe(topics, **subscribe_info)


    def start_consume(self):
        self.run_status = True
        self._consume_message()

    
    def stop_consume(self):
        self.run_status = False


    def _consume_message(self):
        if not self.callback:
            print("callback error")
            return
        counter = 0
        while self.run_status:

            try:
                msg = self.kafka_consumer.poll(timeout=config.KAFKA_POLL_TIMEOUT)

                if msg is None:
                    my_logger.info(f"msg is None")
                    time.sleep(config.KAFKA_POLL_NONE_SLEEP)
                    continue

                if msg.error():
                    raise KafkaException(msg.error())
                
                my_logger.debug(f"message info: {{ \
                                    topic:{msg.topic()}, \
                                    partition:{msg.partition()}, \
                                    offset:{msg.offset()}, \
                                    key:{str(msg.key())}, \
                                    value:{str(msg.value())} \
                                }}  ")              

                self.callback(msg)
                
                self.kafka_consumer.store_offsets(msg)
                counter+=1
                if counter >= config.KAFKA_COMMIT_PER:
                    self.kafka_consumer.commit()
                    counter = 0

            except Exception as e:
                import traceback
                traceback.print_exc()
                # logger.exception(e)
    
        if self.kafka_consumer:
            self.kafka_consumer.close()


    def _demo(self):
        
        group = "test_topic_consumer_group_0001"

        conf = {'bootstrap.servers': "192.168.43.90:9095", 'group.id': group, 'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest', 'enable.auto.offset.store': False}
        
        
        logger = logging.getLogger('consumer')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)

        
        c = Consumer(conf, logger=logger)
        
        def print_assignment(consumer, partitions):
            print('Assignment:', partitions)

        # Subscribe to topics
        c.subscribe(["test_topic"], on_assign=print_assignment)
        
        try:
            while True:
                msg = c.poll(timeout=1.0)

                
                if msg is None:
                    print(f" msg is None")
                    time.sleep(1)
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    # Proper message
                    sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                    (msg.topic(), msg.partition(), msg.offset(),
                                    str(msg.key())))
                    print(msg.value())
                    # Store the offset associated with msg to a local cache.
                    # Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                    # Explicitly storing offsets after processing gives at-least once semantics.
                    c.store_offsets(msg)
        
        finally:
            # Close down consumer to commit final offsets.
            c.close()


kafka_producer = KafkaProducer()

if __name__ == "__main__":
    # kafka_producer = KafkaProducer()
    kafka_consumer = KafkaConsumer()
    
    