import datetime
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def start_logger_consumer():
    channel.queue_declare(queue='logger')
    channel.exchange_declare(exchange='logger_message', exchange_type='direct')
    channel.queue_bind(exchange='logger_message', queue='logger', routing_key='logger')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='logger', on_message_callback=handle_logger)
    channel.start_consuming()

def handle_logger(ch, method, properties, body):
    log = json.loads(body)
    try:
        with open("output.log", "a") as logger:
            now = datetime.datetime.now()
            logger.write(f"{now} - {log['type'].upper()} ----- {log['message']}\n")
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)
