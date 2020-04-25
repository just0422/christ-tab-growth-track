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

pco_thread = threading.Thread(target=pco.start_rabbit_consumer)
pco_thread.start()


@app.route("/disc")
def disc():
    choices = ["Never", "Rarely", "Sometimes", "Often", "Always"]

    return render_template("disc.html", type_details=constants.disc_type_details, choices=choices)
    
@app.route("/disc/submit", methods = ["POST"])
def disc_submit():
    disc_results = {}
    
    for types in constants.disc_type_details:
        disc_results[types] = {
            'id': constants.disc_type_details[types]['id'],
            'value': 0
        }
        for index in range(len(constants.disc_type_details[types]['questions'])):
            disc_results[types]['value'] += int(request.form.get(types + '-' + str(index)))

    maxType1 = list(constants.disc_type_details.keys())[0]
    for typeKey, details in disc_results.items():
        if details['value'] > disc_results[maxType1]['value']:
            maxType1 = typeKey

    remaining = list(constants.disc_type_details.keys())
    remaining.remove(maxType1)
    maxType2 = remaining[0]
    for typeKey in remaining:
        if disc_results[typeKey]['value'] > disc_results[maxType2]['value']:
            maxType2 = typeKey

    doubleMax = []
    if disc_results[maxType1]['value'] == disc_results[maxType2]['value']:
        doubleMax = [maxType1, maxType2]
    
    channel.basic_publish(exchange='', routing_key='pco', body=json.dumps(disc_results))

    return render_template("disc_complete.html", 
        type_details=constants.disc_type_details,
        disc_results=disc_results,
        doubleMax=doubleMax,
        maxType1=maxType1,
        maxType2=maxType2
    )

@app.route("/sga")
def sga():
    choices = ["Almost Never", "Sometimes", "Almost Always"]
    return render_template("sga.html", type_details=constants.sga_type_details, choices=choices)
    
@app.route("/sga/submit", methods = ["POST"])
def sga_submit():
    type_values = {}

    for types in constants.sga_type_details:
        type_values[types] = 0
        for index in range(len(constants.sga_type_details[types]['questions'])):
            type_values[types] += int(request.form.get(types + '-' + str(index)))

    max_types = []
    remaining = list(constants.sga_type_details.keys())
    counter = 9
    while len(max_types) < 3 and counter > 1:
        types = [key for key,val in constants.sga_type_details.items() if type_values[key] == counter]
        max_types += types
        counter -= 1

    return render_template("sga_complete.html", 
        type_values=type_values,
        type_details=constants.sga_type_details,
        max_types = max_types
    )

def find_max_assessment_results(max_result):
    results = {}

    for types in test_properties:

if __name__ == "__main__":
    app.run(debug=True)
