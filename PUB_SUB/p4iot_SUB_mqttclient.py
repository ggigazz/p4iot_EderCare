import paho.mqtt.client as mqtt  # import the client1
import json
import requests
from datetime import datetime


############
def on_message(client, userdata, message):
    with open("log.txt", "a") as file:
        # try:
        # 	print("message received: ", str(message.payload.decode("utf-8")), datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # except:
        # 	print("message not decoded due to error")
        data = json.loads(message.payload)
        url = f"https://api.thingspeak.com/update?api_key={data['api_key']}"
        # Make GET request with data
        response = requests.get(url, data=data)

        # Check response status code (200 = success)
        if response.status_code == 200:
            print("Dati inviati con successo a ThingSpeak.")
        else:
            print(
                "Errore nell'invio dei dati a ThingSpeak. Codice di stato:",
                response.status_code,
            )

        # log in file
        file.write(
            str(message.topic)
            + " "
            + str(message.qos)
            + " "
            + str(message.payload.decode("utf-8"))
            + " "
            + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            + "\n"
        )
        print("message topic =", message.topic)
        print("message qos =", message.qos)
        print("message retain flag =", message.retain)


########################################
# Retrieve broker port, connection username/password
def get_config_sub():
    filename = "./config.json"
    dictionary = json.load(open(filename))
    broker_address = dictionary["broker_address"]
    port = dictionary["port"]
    user = dictionary["user"]
    password = dictionary["password"]

    return broker_address, port, user, password

broker_address, port, user, password = get_config_sub()

# Create new instance
print("creating new instance")
client = mqtt.Client(
    "MQTTClientSUBThingSpeak", clean_session=False
)
# Set username and password
client.username_pw_set(user, password=password)

# Set callback function
client.on_message = on_message
print("connecting to broker")
# Connect to broker
client.connect(broker_address, port=port)
# client.loop_start()
topic = "P4IOT/PATIENT/#"
print("Subscribing to topic", topic)
client.subscribe(topic, qos=2)
# Loop forever
client.loop_forever()
