from flask_mail import Message
from flask import render_template
import json
import pika

from app import app, mail
from . import constants

credentials = pika.PlainCredentials('guest', 'guest')
params = pika.ConnectionParameters('localhost', credentials=credentials, heartbeat=50)
connection = pika.BlockingConnection(params)
channel = connection.channel()

def start_rabbit_consumer():
    channel.queue_declare(queue='email')
    channel.exchange_declare(exchange='email_message', exchange_type='direct')
    channel.queue_bind(exchange='email_message', queue='email', routing_key='email_disc')
    channel.queue_bind(exchange='email_message', queue='email', routing_key='email_sga')
    channel.basic_consume(queue='email', on_message_callback=handle_email)
    channel.start_consuming()

def handle_email(ch, method, properties, body):
    with app.app_context():
        results = json.loads(body)

        recipients = [results['email']]
        subject = results['subject']
        body = "RESULTS"

        message = Message(subject=subject, recipients=recipients)
        message.body = render_template("disc_complete.txt", 
            results=results,
            max_categories=max_categories,
            max_sub_categories=max_sub_categories
        )
        message.html = render_template("disc_complete.mail.html", 
            results=results,
            properties=constants.disc_properties,
            max_categories=max_categories,
            max_sub_categories=max_sub_categories
        )
        
        mail.send(message)
        ch.basic_ack(delivery_tag = method.delivery_tag)
