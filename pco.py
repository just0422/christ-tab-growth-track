import json
import os
import pika
import pypco

pco = pypco.PCO(
        os.environ["PCO_KEY"],
        os.environ["PCO_SECRET"]
    )

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def start_rabbit_consumer():
    channel.queue_declare(queue='pco')
    channel.exchange_declare(exchange='pco_message', exchange_type='direct')
    channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_disc')
    channel.queue_bind(exchange='pco_message', queue='pco', routing_key='pco_sga')
    channel.basic_consume(queue='pco', on_message_callback=handle_pco_person, auto_ack=True)
    channel.start_consuming()

def handle_pco_person(ch, method, properties, body):
    results = json.loads(body)
    print(find_person(results['first_name'], results['last_name'], results['email'])) 

    if method.routing_key == 'pco_disc':
        print(body)
    
    if method.routing_key == 'pco_sga':
        print(body)

def find_person(first_name, last_name, email):
    # These go out with every request as a baseline for finding a person
    email_where = { "where[search_name_or_email]": email }

    # Send the request out
    possible_people = list(pco.iterate('/people/v2/people', **email_where))

    for person in possible_people:
        person_attrs = person['data']["attributes"]
        first_name_matches = first_name in [person_attrs["first_name"], person_attrs["given_name"]]
        last_name_matches = first_name == person_attrs["last_name"]
        
        # Return the id if the person is found
        if first_name_matches and last_name_matches:
            return person["data"]["id"]

    # These go out with every request as a baseline for finding a person
    name_where = { "where[search_name]": f"{first_name} {last_name}" } 

    # Send the request out
    possible_people = list(pco.iterate('/people/v2/people', **name_where))

    # Add someone if no one exists
    if len(possible_people) == 1:
        return possible_people[0]["data"]["id"]

    return None

def create_person(first_name, last_name, email):
    template = {
        'first_name': first_name,
        'last_name': last_name
    }

    payload = pco.template('Person', template)
    person = pco.post('/people/v2/people', payload)

    id = person['data']['id']

    template = {
        'address': email,
        'location': "Home"
    }
    payload = pco.template("Email", template)
    
    pco.post(f'/people/v2/people/{id}/emails', payload)

def submit_disc_assessment(results):
    return None
