import pika
import os
import sys
import logging


class RabbitObject:
    def __init__(self, config):
        self.hostname = config["RabbitMQ"]["Hostname"]
        self.port = config["RabbitMQ"]["Port"]
        self.analysis_queue = config["RabbitMQ"]["Queue"]["Analysis"]
        self.manual_queue = config["RabbitMQ"]["Queue"]["Analysis"]
        self.error_queue = config["RabbitMQ"]["Queue"]["Error"]
        self.connection = None
        self.channel = None

    def connect(self) -> None:
        if self.port != "":
            parameters = pika.ConnectionParameters(self.hostname, self.port)
        else:
            parameters = pika.ConnectionParameters(self.hostname)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def start_working(self, function) -> None:
        self.connect()

        try:
            self.channel.queue_declare(queue=self.analysis_queue, durable=True)
            self.channel.basic_consume(queue=self.analysis_queue, on_message_callback=function, auto_ack=True)
        except ValueError:
            logging.critical('Error while trying to create/connect to channel!')
            try:
                sys.exit(1)
            except SystemExit:
                os.exit(1)

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
        go_over = False
        manual_channel = None
        try:
            manual_channel = self.connection.channel()
            manual_channel.queue_declare(queue=self.manual_queue, durable=True)
        except ValueError:
            logging.error("Error while sending message to error queue!")
            logging.error("\t" + mssg)
            go_over = True
        if go_over:
            manual_channel.basic_publish(exchange='', routing_key=self.manual_queue, body=mssg)
            manual_channel.close()
