import logging
from operator import is_
import requests as req
import matplotlib.pyplot as plt
import json
import telebot  # telebot

from telebot import custom_filters
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup  # Manages Keyboard
from telebot.handler_backends import State, StatesGroup, ContinueHandling  # States
from datetime import datetime
from time import sleep

# States storage
from telebot.storage import StateMemoryStorage


# Pass storage to bot.
state_storage = StateMemoryStorage()


# Telegram bot details
token = '6632156369:AAGXe1HMxfBM-56CgcKErtm2VjfhkbZW8rw'

# DB API URL and port
URL = 'adlab.m2madgenera.com'
PORT = 4367

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class States(StatesGroup):
    """Define the states of the bot"""
    adduser_name = State()
    adduser_surname = State()
    adduser_role = State()
    adduser_channel = State()
    adduser_cf = State()
    adduser_pwd = State()
    adduser_medic = State()
    adduser_final = State()
    managecaregivers_cf = State()
    managecaregivers_caregivers = State()
    managecaregivers_final = State()
    getlist = State()
    getgraph_cf = State()
    getgraph_pwd = State()
    getgraph_nres = State()
    getgraph_final = State()


# Define the bot
state_storage = StateMemoryStorage()  # Init state storage

# Create the Application and pass it bot's token.
bot = telebot.TeleBot(token, state_storage=state_storage)


# Define a function to start the conversation
@bot.message_handler(commands=['start'])
def start(msg):
    # Create a message with available commands
    reply = f"Hi {msg.from_user.full_name}!\n\nHere are the available commands:\n"
    reply += "/adduser - Add new patient\n"
    reply += "/mngcaregivers - Update caregivers to a patient already created\n"
    reply += "/getlist - Get patients list\n"
    reply += "/getgraph - Get graphs about vital signs of a patient\n"
    reply += "/cancel - End the conversation\n"

    markup = ReplyKeyboardMarkup()
    markup.add('/adduser', '/mngcaregivers',
               '/getlist', '/getgraph', '/cancel')
    bot.reply_to(msg, reply, reply_markup=markup)

# Define functions for each other command

# Define a function to add a new user


@bot.message_handler(commands=['adduser'])
def adduser(msg):
    print("DBG adduser function called")
    bot.set_state(msg.from_user.id, States.adduser_name, msg.chat.id)
    bot.reply_to(msg, "Tell me the name of the user")


@bot.message_handler(state=States.adduser_name, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def adduser_name(msg):
    print("DBG adduser_name function called")
    name = msg.text
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_name'] = name
    bot.reply_to(msg, f"Tell me the surname of {adduser_data['adduser_name']}")
    bot.set_state(msg.from_user.id, States.adduser_surname, msg.chat.id)


@bot.message_handler(state=States.adduser_surname, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def adduser_surname(msg):
    print("DBG adduser_surname function called")
    surname = msg.text
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_surname'] = surname
    bot.reply_to(
        msg, f"Tell me the role (medic, patient) of {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
    bot.set_state(msg.from_user.id, States.adduser_role, msg.chat.id)


@bot.message_handler(state=States.adduser_role, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def adduser_role(msg):
    print("DBG adduser_role function called")
    role = msg.text
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_role'] = role
    if (role == "patient"):
        bot.reply_to(
            msg, f"Tell me the thingspeak channel id of {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
        bot.set_state(msg.from_user.id, States.adduser_channel, msg.chat.id)
    else:
        bot.reply_to(
            msg, f"Tell me the CF of {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
        bot.set_state(msg.from_user.id, States.adduser_cf, msg.chat.id)


@bot.message_handler(state=States.adduser_channel, is_digit=True, func=lambda msg: msg.text.startswith('/') == False)
def adduser_channel(msg):
    print("DBG adduser_channel function called")
    channel = msg.text
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_channel'] = channel
        bot.reply_to(
            msg, f"Tell me the CF of {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
        bot.set_state(msg.from_user.id, States.adduser_cf, msg.chat.id)


@bot.message_handler(state=States.adduser_cf, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def adduser_cf(msg):
    print("DBG adduser_cf function called")
    cf = msg.text.upper()
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_cf'] = cf
        if (adduser_data['adduser_role'] == "patient"):
            bot.reply_to(
                msg, f"Tell me the passkey of {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
            bot.set_state(msg.from_user.id, States.adduser_pwd, msg.chat.id)
        else:
            bot.reply_to(
                msg, f"Performing add of the medic {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
            sleep(1)
            bot.set_state(msg.from_user.id, States.adduser_final, msg.chat.id)
            return ContinueHandling()


@bot.message_handler(state=States.adduser_pwd, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def adduser_pwd(msg):
    print("DBG adduser_pwd function called")
    pwd = msg.text
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        adduser_data['adduser_pwd'] = pwd
        bot.reply_to(
            msg, f"Performing add of the patient {adduser_data['adduser_surname']} {adduser_data['adduser_name']}")
    return ContinueHandling()


@bot.message_handler(state=States.adduser_final)
def adduser_final(msg):
    print("DBG adduser_final function called")

    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as adduser_data:
        tobeInserted = dict()
        tobeInserted['name'] = adduser_data['adduser_name']
        tobeInserted['surname'] = adduser_data['adduser_surname']
        tobeInserted['role'] = adduser_data['adduser_role']
        try:
            tobeInserted['thingspeak_channel'] = adduser_data['adduser_channel']
        except Exception:
            tobeInserted['thingspeak_channel'] = ""
        tobeInserted['cf'] = adduser_data['adduser_cf']
        try:
            tobeInserted['passkey'] = adduser_data['adduser_pwd']
        except Exception:
            tobeInserted['passkey'] = ""
        try:
            tobeInserted['medic_cf'] = adduser_data['adduser_medic']
        except Exception:
            tobeInserted['medic_cf'] = ""

        # Use requests to post to an api with the string as an argument
        reply = req.post(
            url=f'http://{URL}:{PORT}/p4iot/api/add_user', json=tobeInserted)
        if reply.status_code == 200:
            bot.send_message(msg.chat.id, reply.json()['data'])
        else:
            bot.send_message(msg.chat.id, "Something went wrong!")
    bot.delete_state(msg.from_user.id, msg.chat.id)
    return


@bot.message_handler(commands=['mngcaregivers'])
def manage_caregivers(msg):
    print("DBG managecaregivers function called")
    bot.set_state(msg.from_user.id, States.managecaregivers_cf, msg.chat.id)
    bot.reply_to(msg, "Tell me the CF of the patient to be updated")


@bot.message_handler(state=States.managecaregivers_cf, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def managecaregivers_cf(msg):
    print("DBG managecaregivers_cf function called")
    cf = msg.text.upper()
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as caregivers_data:
        caregivers_data['caregivers_cf'] = cf
    bot.reply_to(
        msg, "Tell me the phones of the caregivers separated by spaces")
    bot.set_state(msg.from_user.id,
                  States.managecaregivers_caregivers, msg.chat.id)


@bot.message_handler(state=States.managecaregivers_caregivers, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def managecaregivers_caregivers(msg):
    print("DBG managecaregivers_caregivers function called")
    caregivers = msg.text.split()
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as caregivers_data:
        caregivers_data['caregivers_caregivers'] = caregivers
        bot.reply_to(
            msg, f"Performing update of the caregivers of the patient {caregivers_data['caregivers_cf']}")
    bot.set_state(msg.from_user.id, States.managecaregivers_final, msg.chat.id)
    return ContinueHandling()


@bot.message_handler(state=States.managecaregivers_final)
def managecaregivers_final(msg):
    print("DBG managecaregivers_final function called")
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as caregivers_data:
        tobeInserted = dict()
        tobeInserted['cf'] = caregivers_data['caregivers_cf']
        tobeInserted['numbers'] = caregivers_data['caregivers_caregivers']
        # Use requests to post to an api with the string as an argument
        reply = req.put(
            url=f'http://{URL}:{PORT}/p4iot/api/upd_caregivers', json=tobeInserted)
        if reply.status_code == 200:
            bot.send_message(msg.chat.id, reply.json()['data'])
        else:
            bot.send_message(msg.chat.id, "Something went wrong!")
    bot.delete_state(msg.from_user.id, msg.chat.id)
    return


# Define a function to get the list of patients
@bot.message_handler(commands=['getlist'])
def getlist(msg):
    try:
        reply = req.get(url=f'http://{URL}:{PORT}/p4iot/api/get_users')
        if reply.status_code == 200:
            user_list = reply.json()['data']
            user_dict = dict()
            user_dict['users'] = []
            for row in user_list:
                row.pop(0)
                user_dict['users'].append(row)
            bot.reply_to(msg, json.dumps(user_dict, indent = 2))
        else:
            bot.reply_to(msg, "Something went wrong!")
    except ConnectionError:
        bot.reply_to(msg, "Error in connection to DB")


# Define a function to get the graph of a patient
@bot.message_handler(commands=['getgraph'])
def getgraph(msg):
    print("DBG getgraph function called")
    bot.set_state(msg.from_user.id, States.getgraph_cf, msg.chat.id)
    bot.reply_to(msg, "Tell me the CF of the patient")


@bot.message_handler(state=States.getgraph_cf, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def getgraph_cf(msg):
    print("DBG getgraph_cf function called")
    cf = msg.text.upper()
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['graph_cf'] = cf
    bot.reply_to(msg, "Tell me the passkey of the patient")
    bot.set_state(msg.from_user.id, States.getgraph_pwd, msg.chat.id)


@bot.message_handler(state=States.getgraph_pwd, is_digit=False, func=lambda msg: msg.text.startswith('/') == False)
def getgraph_pwd(msg):
    print("DBG getgraph_pwd function called")
    pwd = msg.text.upper()
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['graph_pwd'] = pwd
    bot.reply_to(msg, "Tell me the number of results")
    bot.set_state(msg.from_user.id, States.getgraph_nres, msg.chat.id)


@bot.message_handler(state=States.getgraph_nres, is_digit=True, func=lambda msg: msg.text.startswith('/') == False)
def getgraph_nres(msg):
    print("DBG getgraph_nres function called")
    nres = int(msg.text)
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['graph_nres'] = nres
    bot.reply_to(msg, "Generating graph")
    bot.set_state(msg.from_user.id, States.getgraph_final, msg.chat.id)
    return ContinueHandling()


@bot.message_handler(state=States.getgraph_final)
def getgraph_final(msg):
    print("DBG getgraph_final function called")
    graph_data = bot.retrieve_data(msg.from_user.id, msg.chat.id)
    url = f'http://{URL}:{PORT}/p4iot/api/get_thingspeak_channel/?cf={graph_data.data["graph_cf"]}&pwd={graph_data.data["graph_pwd"]}'
    reply = req.get(url=url)
    if reply.status_code == 200:
        ts_channel = reply.json()['data']
        reply = req.get(
            f'https://api.thingspeak.com/channels/{ts_channel}/feeds.json?api_key={graph_data.data["graph_pwd"]}&results={graph_data.data["graph_nres"]}')
        data = reply.json()

        # Extract field names and data
        field_names = [data["channel"][f"field{i}"] for i in range(1, 6)]
        feed_data = {f"field{i}": [
            float(entry[f"field{i}"]) for entry in data["feeds"]] for i in range(1, 6)}
        datehour_raw = {"datehour": [entry["created_at"]
                                     for entry in data["feeds"]]}
        datehour = {"datehour": [datetime.strptime(datehour_raw["datehour"][i], "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%d/%m/%Y %H:%M") for i in range(len(datehour_raw["datehour"]))]}

        # Create and send separate plots for each field
        for index, field_name in enumerate(field_names):
            plt.figure(figsize=(10, 6), constrained_layout=True)
            plt.plot(feed_data[f"field{index+1}"])
            plt.title(f'{field_name} Data')
            plt.xlabel('Date Hour')
            plt.ylabel(field_name)
            plt.grid(True)
            plt.xticks(
                range(len(feed_data[f"field{index+1}"])), datehour["datehour"], rotation=60)
            plt.locator_params(axis='x', nbins=len(
                feed_data[f"field{index+1}"])//5)

            # Save the plot as an image in memory
            plt.savefig('./graph.png', format='png')

            # Send the image as a reply to the user
            bot.send_photo(msg.chat.id, photo=open('./graph.png', 'rb'))

        # Close the plots
        plt.close('all')
    else:
        bot.send_message(msg.chat.id, "Something went wrong!")
    bot.delete_state(msg.from_user.id, msg.chat.id)
    return


# Define a function to end the conversation
@bot.message_handler(commands=['cancel'])
def cancel(msg):
    print("DBG cancel function called")
    reply = "Conversation is ended. Type /start to display the menu again."
    bot.reply_to(msg, reply, reply_markup=ReplyKeyboardRemove())


# Main function to run the bot
if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())
    # Start the bot
    bot.infinity_polling(skip_pending=True)
