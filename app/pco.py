import json
import os
import pika
import pypco
import time

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
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='pco', on_message_callback=handle_pco_person)
    channel.start_consuming()

def handle_pco_person(ch, method, properties, body):
    try:
        results = json.loads(body)
        request_count = 0

        # Gather Field Data
        person_id = results['person_id']
        field_data_id = get_field_data(person_id, results["id"])
        request_count += 1

        # Send to PCO
        send_field_data(person_id, field_data_id, results)
        request_count += 1

        msg_body = {
            'type': 'info',
            'message': f"pco.py ------- handle_pco_person -- Sending {results['first_name']} {results['last_name']} - {results['property']} -> {results['value']}"
        }
        channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body))

        connection.sleep(0.05 * request_count)
    except Exception as e:
        msg_body_1 = {
            'error': 'error',
            'message': f"pco.py ------- handle_pco_person -- Error sending {results['first_name']} {results['last_name']} - {results['property']} -> {results['value']}"
        }
        channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body_1))
        msg_body_2 = {
            'type': 'error',
            'message': "pco.py ------- handle_pco_person -- " + str(e)
        }
        channel.basic_publish(exchange='logger_message', routing_key='logger', body=json.dumps(msg_body_2))
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)

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

    person_id = person['data']['id']

    template = {
        'address': email,
        'location': "Home"
    }
    payload = pco.template("Email", template)
    
    pco.post(f'/people/v2/people/{person_id}/emails', payload)

    return person_id

def get_field_data(person_id, property_id):
    for field in pco.iterate(f"/people/v2/people/{person_id}/field_data?include=field_definition"):
        if field["data"]["relationships"]["field_definition"]["data"]["id"] == property_id:
            return field["data"]["id"]
    return None

def send_field_data(person_id, field_data_id, result):
    template = {
        "value": result['value'],
        "field_definition_id": result["id"]
    }
    payload = pco.template("FieldDatum", template)

    if field_data_id:
        pco.patch(f'/people/v2/field_data/{field_data_id}', payload)
    else:
        pco.post(f'/people/v2/people/{person_id}/field_data', payload)
