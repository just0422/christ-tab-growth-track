from flask import Flask, render_template, request
import json
import pika
import threading
import sys

import pco
import constants

app = Flask(__name__)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='pco')
channel.exchange_declare(exchange='pco_message', exchange_type='direct')
channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_disc')
channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_sga')

pco_thread = threading.Thread(target=pco.start_rabbit_consumer, daemon=True)
pco_thread.start()


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
    
    message = build_message(disc_results)
    channel.basic_publish(exchange='pco_message', routing_key='pco_disc', body=json.dumps(message))

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

    message = build_message(sga_results)
    channel.basic_publish(exchange='pco_message', routing_key='pco_sga', body=json.dumps(message))
   
    return render_template("sga_complete.html", 
        sga_properties=constants.sga_properties,
        sga_results=sga_results,
        max_categories=max_categories
    )

def build_message(results):
    return {
        'first_name': request.form.get('firstName'),
        'last_name': request.form.get('lastName'),
        'email': request.form.get('emailAddress'),
        'results': results
    }

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


if __name__ == "__main__":
    app.run(debug=True)
