import requests as req
import logging
from datetime import datetime
import json

# DB API URL AND PORT
def get_DB_config():
    filename = "microservices/config.json"
    dictionary = json.load(open(filename))
    URL = dictionary["DB"]["URL"]
    PORT = dictionary["DB"]["PORT"]

    return URL, PORT
URL, PORT = get_DB_config()

# EMERGENCY CALL API URL AND PORT
def get_emergency_config():
    filename = "microservices/config.json"
    dictionary = json.load(open(filename))
    EMER_CALL_URL = dictionary["EMERCENCY"]["URL"]
    EMER_CALL_PORT = dictionary["EMERCENCY"]["PORT"]

    return EMER_CALL_URL, EMER_CALL_PORT


EMER_CALL_URL, EMER_CALL_PORT = get_emergency_config()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# dict of comparison values
accepted_values = {"resting": {"OxygenLevel": {
    "min": 95, "max": 100}, "Temperature": {"min": 35, "max": 38}, "HeartRate": {"min": 60, "max": 100}, "RespiratoryRate": {"min": 10, "max": 20}}, "training": {"OxygenLevel": {
        "min": 92, "max": 100}, "Temperature": {"min": 35, "max": 49}, "HeartRate": {"min": 60, "max": 160}, "RespiratoryRate": {"min": 10, "max": 60}}}


if __name__ == "__main__":
    logging.info("Starting the program")
    # Get the list of all the thinkspeak channels
    ts_channels = req.get(
        f'http://{URL}:{PORT}/p4iot/api/get_all_thingspeak_channel').json()['data']
    logging.info(f"Got {len(ts_channels)} Thingspeak channels")
    patient_health = dict()
    patient_health['id'] = list()
    patient_health['ts_channel'] = list()
    patient_health['key'] = list()

    # For every patient check if is all good or not
    for patient in ts_channels:
        if patient == '':
            ts_channels.pop(patient)
    for patient in ts_channels:
        patient_health['id'].append(patient[0])
        patient_health['ts_channel'].append(patient[1])
        patient_health['key'].append(patient[2])

        # Retrieve values from thingspeak and analyze them
        try:
            reply = req.get(
                f'https://api.thingspeak.com/channels/{patient[1]}/feeds.json?api_key={patient[2]}&results=6')
            reply.raise_for_status()
            data = reply.json()

            # Extract field names and data
            field_names = [data["channel"][f"field{i}"] for i in range(1, 6)]
            feed_data = {f"field{i}": [
                float(entry[f"field{i}"]) for entry in data["feeds"]] for i in range(1, 6)}
            datehour_raw = {"datehour": [
                entry["created_at"] for entry in data["feeds"]]}
            datehour = {"datehour": [datetime.strptime(datehour_raw["datehour"][i], "%Y-%m-%dT%H:%M:%SZ").strftime(
                "%d/%m/%Y %H:%M") for i in range(len(datehour_raw["datehour"]))]}

            # Check if values exceed thresholds. If someone exceed call emergency number, else continue
            accelerometer_position = field_names.index("Accelerometer")
            emergency_called = False
            for index, field_name in enumerate(field_names[:-1]):
                for value in feed_data[f"field{index+1}"]:
                    # if accelerometer signal that patient was in motion, compare with default values for training
                    if feed_data[f"field{accelerometer_position+1}"][index] == 1:
                        # if it is outside boundaries, call emergency number
                        if value < accepted_values["training"][field_name]["min"] or value > accepted_values["training"][field_name]["max"]:
                            reply = req.get(
                                f'http://{URL}:{PORT}/p4iot/api/get_caregivers?id={patient_health["id"][-1]}').json()['data']
                            data = {
                                'to': reply['phones'], 'patient_name': reply['name'] + ' ' + reply['surname']}
                            req.post(
                                f'http://{EMER_CALL_URL}:{EMER_CALL_PORT}/emergency_call', json=data)
                            print("Emergency service called")
                            emergency_called = True
                            break
                        else:
                            # else continue
                            continue
                    # else he/she was resting, so compare with other values
                    else:
                        # if it is outside boundaries, call emergency number
                        if value < accepted_values["resting"][field_name]["min"] or value > accepted_values["resting"][field_name]["max"]:
                            reply = req.get(
                                f'http://{URL}:{PORT}/p4iot/api/get_caregivers?id={patient_health["id"][-1]}').json()['data']
                            data = {
                                'to': reply['phones'], 'patient_name': reply['name'] + ' ' + reply['surname']}
                            req.post(
                                f'http://{EMER_CALL_URL}:{EMER_CALL_PORT}/emergency_call', json=data)
                            print("Emergency service called")
                            emergency_called = True
                            break
                        else:
                            # else continue
                            continue
                # If emergency call has already been made, break the loop and go to next patient
                if emergency_called:
                    break
        except req.exceptions.RequestException as e:
            logging.error(f"Error retrieving data from Thingspeak: {e}")
            continue
