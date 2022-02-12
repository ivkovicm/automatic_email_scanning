import pika
import os
import sys
from other import config_loader


class RabbitObject:
    def __init__(self, config):
        # TODO: play with error
        try:
            self.config = config_loader.RabbitConfiguration(config)
        except:
            pass
        self.connection = None
        self.channel = None

    def connect(self) -> None:
        if self.port != "":
            parameters = pika.ConnectionParameters(self.config.hostname, self.config.port)
        else:
            parameters = pika.ConnectionParameters(self.config.hostname)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def analysis_receive(self, function) -> None:
        self.connect()

        try:
            self.channel.queue_declare(queue=self.config.analysis_queue, durable=True)
            self.channel.basic_consume(queue=self.config.analysis_queue, on_message_callback=function, auto_ack=True)
        except ValueError:
            logging.critical('Error while trying to create/connect to channel!')
            sys.exit(1)

        try:
            logging.info('Started listening for messages!')
            self.channel.start_consuming()
        except KeyboardInterupt:
            logging.info('Keyboard interrupt, stopped processing messages!')
            self.channel.stop_consuming()
        except:
            logging.critical('Error with processing messages from Rabbit!')
            self.channel.stop_consuming()

        self.connection.close()

    def send_to_manual(self, mssg: str) -> None:
        self.connect()
        go_over = False
        manual_channel = None
        try:
            manual_channel = self.connection.channel()
            manual_channel.queue_declare(queue=self.config.manual_queue, durable=True)
        except ValueError:
            logging.error("Error while sending message to error queue!")
            logging.error(mssg)
            go_over = True
        if not go_over:
            manual_channel.basic_publish(exchange='', routing_key=self.config.manual_queue, body=mssg)
            manual_channel.close()

    def send_to_analysis(self, mssg) -> None:
        self.connect()
        analysis_channel = None
        try:
            analysis_channel = self.connection.channel()
            analysis_channel.queue_declare(queue=self.config.analysis_queue, durable=True)
        except ValueError:
            logging.error("Error while sending message to analysis queue!")
            logging.error(mssg)
        analysis_channel.basic_publish(exchange='', routing_key=self.config.analysis_queue, body=mssg)
        analysis_channel.close()

    def send_to_error(self, mssg) -> None:
        self.connect()
        error_channel = None
        try:
            error_channel = self.connection.channel()
            error_channel.queue_declare(queue=self.config.error_queue, durable=True)
        except ValueError:
            logging.error("Error while sending message to error queue!")
            logging.error(mssg)
        error_channel.basic_publish(exchange='', routing_key=self.config.error_queue, body=mssg)
        error_channel.close()

    def verdict_receive(self, function) -> None:
        self.connect()

        try:
            self.channel.queue_declare(queue=self.config.analysis_queue, durable=True)
            self.channel.basic_consume(queue=self.config.analysis_queue, on_message_callback=function, auto_ack=True)
        except ValueError:
            logging.critical('Error while trying to create/connect to channel!')
            sys.exit(1)

        try:
            logging.info('Started listening for messages!')
            self.channel.start_consuming()
        except KeyboardInterupt:
            logging.info('Keyboard interrupt, stopped processing messages!')
            self.channel.stop_consuming()
        except:
            logging.critical('Error with processing verdict messages from Rabbit!')
            self.channel.stop_consuming()

        self.connection.close()