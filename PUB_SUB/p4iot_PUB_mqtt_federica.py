import json
import paho.mqtt.client as mqtt  # import the client
from numpy import random
from time import sleep

# Retrieve broker port, connection username/password and API KEY
def get_config_pub():
    filename = "./config.json"
    dictionary = json.load(open(filename))
    broker_address = dictionary["broker_address"]
    port = dictionary["port"]
    user = dictionary["user"]
    password = dictionary["password"]
    api_key = dictionary["api_key_F"]

    return broker_address, port, user, password, api_key

broker_address, port, user, password, api_key = get_config_pub()

print("creating new instance")
client = mqtt.Client("MQTTClientPUBFederica",
                     clean_session=False)  # create new instance
client.username_pw_set(user, password=password)  # set username and password
print("connecting to broker")
client.connect(broker_address, port=port)  # connect to broker
client.loop_start()  # start the loop
topic = f"P4IOT/PATIENT/{api_key}"
# field 1 power
field1 = 100 * random.power(99)
# field 2 triangular
field2 = random.triangular(37, 37.3, 39)
# field 3 triangular
field3 = random.triangular(50, 80, 145)
# field 4 laplace
field4 = random.laplace(15, 1)
# field 5 randint
field5 = random.randint(0, 1)
while (1):
    # at each iteration take the fields above, add or subtract a uniform closer and publish them. If they exceed a given threshow they shoud be normalized
    field1 = field1 + random.uniform(-0.2, 0.2)
    field2 = field2 + random.uniform(-0.1, 0.1)
    field3 = field3 + random.uniform(-1, 1)
    field4 = field4 + random.uniform(-0.3, 0.3)
    field5 = random.randint(0, 1)
    # make sure not to exit from boundaries
    if field1 > 99:
        field1 = 99
    elif field1 < 94:
        field1 = 94
    if field2 > 39:
        field2 = 39
    elif field2 < 35:
        field2 = 35
    if field3 > 200:
        field3 = 200
    elif field3 < 50:
        field3 = 50
    if field4 > 40:
        field4 = 40
    elif field4 < 12:
        field4 = 12
    # Dati da inviare al canale ThingSpeak
    data = {'api_key': api_key, 'field1': field1, 'field2': field2,
            'field3': field3, 'field4': field4, 'field5': field5}

    print("Publishing message to topic", topic)
    client.publish(topic, json.dumps(data), qos=2)
    sleep(5)  # busy waiting


client.loop_stop()  # stop the loop
