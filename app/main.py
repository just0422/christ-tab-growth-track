from flask import render_template, request
import json
import pika
import threading
import sys

from app import app
from . import constants
from . import gt_email
from . import logger
from . import pco

params = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='pco')
channel.queue_declare(queue='email')
channel.queue_declare(queue='logger')
channel.exchange_declare(exchange='pco_message', exchange_type='direct')
channel.exchange_declare(exchange='email_message', exchange_type='direct')
channel.exchange_declare(exchange='logger_message', exchange_type='direct')
channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_disc')
channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_sga')
channel.queue_bind(exchange='email_message', queue='email', routing_key='email_disc')
channel.queue_bind(exchange='email_message', queue='email', routing_key='email_sga')
channel.queue_bind(exchange='logger_message', queue='logger', routing_key='logger')
channel.close()
connection.close()

pco_thread = threading.Thread(target=pco.start_rabbit_consumer, daemon=True)
email_thread = threading.Thread(target=gt_email.start_rabbit_consumer, daemon=True)
logging_thread = threading.Thread(target=logger.start_logger_consumer, daemon=True)

pco_thread.start()
email_thread.start()
logging_thread.start()

@app.errorhandler(404)
def page_not_found(error):
    return 'This route does not exist {}'.format(request.url), 404

@app.route("/disc")
def disc():
    choices = ["Never", "Rarely", "Sometimes", "Often", "Always"]

    return render_template("disc.html", 
        disc_properties=constants.disc_properties, 
        choices=choices
    )
    
@app.route("/disc/submit", methods = ["POST"])
def disc_submit():
    disc_results = assessment_results(constants.disc_properties)
    max_categories = filter_max_categories(constants.disc_properties, disc_results, 1, 25)
   
    max_sub_categories = list()
    if len(max_categories) > 1:
        max_sub_categories = max_categories
    else:
        max_category_value = disc_results[max_categories[0]]['value'] - 1
        max_sub_categories = filter_max_categories(constants.disc_properties, disc_results, 1, max_category_value)
    
    send_message(disc_results, 'pco_message', 'pco_disc')
    #send_email(disc_results, 'DISC', 'disc', max_categories, max_sub_categories)

    return render_template("disc_complete.html", 
        disc_properties=constants.disc_properties,
        disc_results=disc_results,
        max_categories=max_categories,
        max_sub_categories=max_sub_categories
    )

@app.route("/sga")
def sga():
    choices = ["Almost Never", "Sometimes", "Almost Always"]
    return render_template("sga.html", 
        sga_properties=constants.sga_properties, 
        choices=choices
    )
    
@app.route("/sga/submit", methods = ["POST"])
def sga_submit():
    sga_results = assessment_results(constants.sga_properties)
    max_categories = filter_max_categories(constants.sga_properties, sga_results, 3, 9)

    send_message(sga_results, 'pco_message', 'pco_sga')
    send_email(sga_results, 'Spiritual Gift', 'sga', max_categories)
   
    return render_template("sga_complete.html", 
        sga_properties=constants.sga_properties,
        sga_results=sga_results,
        max_categories=max_categories
    )

def send_message(results, exchange, routing_key):
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('emailAddress')

    base_message = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }
    
    person_id = pco.find_person(first_name, last_name, email)
    msg_body = None
    if person_id:
        msg_body = {
            'type': 'info',
            'message': f"pco.py ------- handle_pco_person -- Found Profile {first_name} {last_name} ({email}) -- ({person_id}) "
        }
    else:
        person_id = pco.create_person(first_name, last_name, email)
        msg_body = {
            'type': 'info',
            'message': f"pco.py ------- handle_pco_person -- Created Profile {first_name} {last_name} ({email}) -- ({person_id}) "
        }
    channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body))

    msg_body = {
        'type': 'info',
        'message': f"main.py ------ send_message ------- Sending {routing_key} messages for {first_name} {last_name} message"
    }
    channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body))
    for prop, results in results.items():
        message = base_message.copy()
        message['person_id'] = person_id
        message['property'] = prop
        message['id'] = results['id']
        message['value'] = results['value']

        msg_body = {
            'type': 'info',
            'message': f"main.py ------ send_message ------- Sending {first_name} {last_name} -- {message['property']} ({message['value']})"
        }
        channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body))
        channel.basic_publish(exchange='pco_message', routing_key=routing_key, body=json.dumps(message))
    channel.close()
    connection.close()

def send_email(results, subject, routing_key, max_categories, max_sub_categories=[]):
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    message = {
        'first_name': request.form.get('firstName'),
        'last_name': request.form.get('lastName'), 
        'email': request.form.get('emailAddress'),
        'subject': f"Your {subject} Assessment results",
        'results': results,
        'max_categories': max_categories,
        'max_sub_categories': max_sub_categories
    }

    msg_body = {
        'type': 'info',
        'message': f"main.py ------ send_email --------- Sending {routing_key} message for {request.form.get('firstName')} {request.form.get('lastName')} Email"
    }
    channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body))
    channel.basic_publish(exchange='email_message', routing_key=f"email_{routing_key}", body=json.dumps(message))
    channel.close()
    connection.close()

def assessment_results(properties):
    results = {}

    for category in properties:
        results[category] = {
            'id': properties[category]['id'],
            'value': 0
        }
        for index in range(len(properties[category]['questions'])):
            results[category]['value'] += int(request.form.get(category + '-' + str(index)))
    
    return results

def filter_max_categories(properties, results, max_categories_count, max_category_value):
    max_categories = list()
    counter = max_category_value
    while len(max_categories) < max_categories_count and counter > 1:
        categories = [category for category in properties if results[category]['value'] == counter]

        max_categories += categories
        counter -= 1

    return max_categories


