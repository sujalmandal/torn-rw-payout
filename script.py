import csv
import os
import time
from datetime import timezone, datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests

# constant definitions
API_KEY = os.getenv('TORN_API_KEY_ENV')
FILE_NAME = "output.csv"
MASTER_FILE_NAME = "all_attacks.csv"
LOST = 'lost'
DEFENDER_NAME = 'defender_name'
DEFENDER_ID = 'defender_id'
GAINED = 'gained'
RESPECT = 'respect'
CHAIN_BONUS = 'chain_bonus'
MODIFIERS = 'modifiers'
ATTACKER_NAME = 'attacker_name'
ATTACKER_ID = 'attacker_id'
DEFENDER_FACTION = 'defender_faction'
DEFENDER_FACTION_NAME = 'defender_factionname'
ATTACKER_FACTION_NAME = 'attacker_factionname'
RANKED_WAR = 'ranked_war'
TIMESTAMP_STARTED = 'timestamp_started'
ATTACKS_KEY = 'attacks'
OUTSIDE_ATTACKS_KEY = 'outside_attacks'
NAME_KEY = 'name'
MODIFIER_KEY = "modifiers"
RESPECT_GAINED_KEY = "gained"
RESPECT_LOST_KEY = "lost"
CODE = "code"
TIMESTAMP_ENDED = "timestamp_ended"
ATTACKER_FACTION = "attacker_faction"
ATTACKER_FACTIONNAME = "attacker_factionname"
DEFENDER_FACTIONNAME = "defender_factionname"
RESULT = "result"
STEALTHED = "stealthed"
CHAIN = "chain"
RAID = "raid"
RESPECT_GAIN = "respect_gain"
RESPECT_LOSS = "respect_loss"
FAIR_FIGHT = "fair_fight"
WAR = "war"
RETALIATION = "retaliation"
GROUP_ATTACK = "group_attack"
OVERSEAS = "overseas"

SELECTED_ATTACK_KEY = [
    CODE,
    TIMESTAMP_STARTED,
    TIMESTAMP_ENDED,
    ATTACKER_ID,
    ATTACKER_NAME,
    ATTACKER_FACTION,
    ATTACKER_FACTIONNAME,
    DEFENDER_ID,
    DEFENDER_NAME,
    DEFENDER_FACTION,
    DEFENDER_FACTIONNAME,
    RESULT,
    STEALTHED,
    RESPECT,
    CHAIN,
    RAID,
    RANKED_WAR,
    RESPECT_GAIN,
    RESPECT_LOSS,
    MODIFIERS,
]

MODIFIER_ATTRIBUTES = [
    FAIR_FIGHT,
    WAR,
    RETALIATION,
    GROUP_ATTACK,
    OVERSEAS,
    CHAIN_BONUS
]
# all attacks
attacks_master_list = []

HEADER = ['id', 'name', 'attacks', 'outside_attacks', 'gained', 'lost']

extra_calls = [',applications', ',armor', ',armorynews', ',attacknews',
               ',basic', ',boosters', ',cesium', ',chain', ',chainreport',
               ',chains', ',contributors', ',crimenews', ',crimes',
               ',currency', ',donations', ',drugs', ',fundsnews',
               ',mainnews', ',medical', ',membershipnews', ',positions',
               ',reports', ',revives', ',revivesfull', ',stats', ',temporary',
               ',territory', ',territorynews', ',timestamp', ',upgrades', ',weapons '
               ]


def index_of(key):
    return SELECTED_ATTACK_KEY.index(key)


def index_of_mod(key):
    return len(SELECTED_ATTACK_KEY) + MODIFIER_ATTRIBUTES.index(key) - 1


def visualize_report():
    # Create a dataframe from the data
    df = pd.read_csv('output.csv')

    # Sort the dataframe by the "attacks" column
    df = df.sort_values(by='attacks', ascending=False)
    plt.figure(figsize=(12, 6))
    # bars = plt.bar(df['name'], df['attacks'], df['lost'], df['outside_attacks'])

    # Create a bar chart of the "attacks" column
    plt.bar(df['name'], df['attacks'], width=0.5)
    plt.xticks(rotation=90)
    plt.xlabel('Name')
    plt.ylabel('Attacks')
    plt.title('Attacks by Name')

    # Get the bleeders
    bleeders = df[df['lost'] > df['gained']].sort_values(by='lost', ascending=False)

    # Get names and lost values
    names = bleeders['name']
    lost = bleeders['lost']

    # Create the bar graph
    plt.figure(figsize=(12, 6))
    plt.bar(names, lost, width=0.5)
    plt.xticks(rotation=90)
    plt.xlabel('Name')
    plt.ylabel('Lost')
    plt.title('Bleeders')
    plt.show()


def get_start_time_end_time(text):
    # Extract start and end times
    start_str, end_str = text.strip().split(" until ")
    start_time = datetime.strptime(start_str, "%H:%M:%S - %d/%m/%y")
    end_time = datetime.strptime(end_str, "%H:%M:%S - %d/%m/%y")

    # Convert start and end times to epoch time
    start_time_epoch = int(start_time.timestamp())
    end_time_epoch = int(end_time.timestamp())
    return {start_time_epoch, end_time_epoch}


def is_ranked_war_attack(attack_obj):
    return eval(attack_obj[index_of(RANKED_WAR)]) == 1


def get_timestamp(start_day, start_hour, start_min, month, year):
    return int(datetime(year, month, start_day, start_hour, start_min, tzinfo=timezone.utc).timestamp())


def save_summary(scores):
    with open(FILE_NAME, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(HEADER)
        for member in scores:
            writer.writerow([member, scores[member][NAME_KEY], scores[member][ATTACKS_KEY],
                             scores[member][OUTSIDE_ATTACKS_KEY], scores[member][RESPECT_GAINED_KEY],
                             scores[member][RESPECT_LOST_KEY]])


### LOAD THE LIST OF ATTACKS ###
def load_list():
    try:
        with open("all_attacks.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            my_list = list(reader)
            print("loaded from previously cached file")
            return my_list
    except FileNotFoundError:
        print("all_attacks.csv not found")
        return None


### PERSIST THE ATTACKS ###
def save_list(list):
    print(f"total number of attacks (in + out)-> {len(list)}")
    with open(MASTER_FILE_NAME, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        headers = SELECTED_ATTACK_KEY
        headers.remove(MODIFIER_KEY)
        headers.extend(MODIFIER_ATTRIBUTES)
        writer.writerow(headers)
        for attack in list:
            writer.writerow([
                # main attributes
                attack[CODE], attack[TIMESTAMP_STARTED], attack[TIMESTAMP_ENDED],
                attack[ATTACKER_ID], attack[ATTACKER_NAME], attack[ATTACKER_FACTION],
                attack[ATTACKER_FACTIONNAME], attack[DEFENDER_ID], attack[DEFENDER_NAME],
                attack[DEFENDER_FACTION], attack[DEFENDER_FACTIONNAME], attack[RESULT],
                attack[STEALTHED], attack[RESPECT], attack[CHAIN],
                attack[RAID], attack[RANKED_WAR], attack[RESPECT_GAIN], attack[RESPECT_LOSS],
                # modifiers
                attack[MODIFIER_KEY][FAIR_FIGHT], attack[MODIFIER_KEY][WAR], attack[MODIFIER_KEY][RETALIATION],
                attack[MODIFIER_KEY][GROUP_ATTACK], attack[MODIFIER_KEY][OVERSEAS], attack[MODIFIER_KEY][CHAIN_BONUS]
            ])


### PROCESS THE ATTACK ROWS ###
def process_attacks(hero_faction_name, enemy_faction_name, master_list):
    print(f"going to process total {len(master_list)} records.")

    count = 0
    outgoing = 0
    incoming = 0
    is_header = False

    scores = {}

    for attack_obj in master_list:
        if is_header is False:
            is_header = True
            continue
        # increment counter
        count += 1
        _id = attack_obj[index_of(CODE)]
        if _id == "033fd2e28fb1242f0e5f3d081daebf58":
            print("*****")
        is_rw_attack = is_ranked_war_attack(attack_obj)
        attacker_fac_name = attack_obj[index_of(ATTACKER_FACTION_NAME)]
        defender_fac_name = attack_obj[index_of(DEFENDER_FACTION_NAME)]

        print(f"count: {count} id: {_id},  attacking fac : {attacker_fac_name}, defending fac : {defender_fac_name}, "
              f"is_rw_attack : {is_rw_attack}")

        # outside hits
        if attacker_fac_name == hero_faction_name and defender_fac_name != enemy_faction_name:
            # create a new record if not encountered before
            attacker_id = attack_obj[index_of(ATTACKER_ID)]

            # create entry if not exists
            if attacker_id not in scores.keys():
                print(f"id: {_id} registered as outside hit")
                attacker_name = attack_obj[index_of(ATTACKER_NAME)]
                scores[attacker_id] = {NAME_KEY: attacker_name, ATTACKS_KEY: 0, OUTSIDE_ATTACKS_KEY: 0, GAINED: 0,
                                       LOST: 0}
            # update existing record
            scores[attacker_id][OUTSIDE_ATTACKS_KEY] += 1
            outgoing += 1
            continue

        # attack is against enemy faction and made by hero faction
        if defender_fac_name == enemy_faction_name and is_rw_attack:

            # create a new record if not encountered before
            if attack_obj[index_of(ATTACKER_ID)] not in scores.keys():
                print(f"id: {_id} registered as rw attack")
                scores[attack_obj[index_of(ATTACKER_ID)]] = {'name': attack_obj[index_of(ATTACKER_NAME)], 'attacks': 0,
                                                             'outside_attacks': 0, 'gained': 0, 'lost': 0}
            # update existing record
            if eval(attack_obj[index_of_mod(CHAIN_BONUS)]) < 10:
                scores[attack_obj[index_of(ATTACKER_ID)]][GAINED] += eval(attack_obj[index_of(RESPECT)])
                scores[attack_obj[index_of(ATTACKER_ID)]][ATTACKS_KEY] += 1
                outgoing += 1
            continue

        # attack is against hero faction and made by target enemy faction
        if defender_fac_name == hero_faction_name and is_rw_attack:
            # create a new record if not encountered before
            if attack_obj[index_of(DEFENDER_ID)] not in scores.keys():
                print(f"id: {_id} registered as rw defend")
                scores[attack_obj[index_of(DEFENDER_ID)]] = {'name': attack_obj[index_of(DEFENDER_NAME)], 'attacks': 0,
                                                             'outside_attacks': 0, 'gained': 0, 'lost': 0}
            # update existing record
            if eval(attack_obj[index_of_mod(CHAIN_BONUS)]) < 10:
                scores[attack_obj[index_of(DEFENDER_ID)]][LOST] += eval(attack_obj[index_of(RESPECT)])
                incoming += 1
                continue

    print(f'Total hits made: {outgoing}')
    print(f'Total hits received: {incoming}')

    return scores


#### CALL API TO LOAD ATTACKS ###
def fetch_attacks(end_stamp, start_stamp, api_key):
    next_call_stamp = start_stamp
    processed_attack_records = []
    count = 0
    print('fetching attacks using API ...')

    while next_call_stamp <= end_stamp:
        count += 1
        time.sleep(2)
        # print(f'{next_call_stamp}')
        request = requests.get(
            f'https://api.torn.com/faction/?selections=attacks'
            f'{extra_calls[count % len(extra_calls)]}&from={next_call_stamp}&key={api_key}')

        response_body = request.json()
        # attack object found
        try:
            attacks_list = response_body[ATTACKS_KEY]

            for attack_id in attacks_list:
                # update timestamp to set the next 'from' field in the API call
                attack_obj = attacks_list[attack_id]
                if attack_obj[TIMESTAMP_STARTED] > next_call_stamp:
                    next_call_stamp = attack_obj[TIMESTAMP_STARTED] - 1

                if attack_id not in processed_attack_records:
                    processed_attack_records.append(attack_id)
                    # is_rw_attack = is_ranked_war_attack(attack_id, attacks_list)
                    # prepare a master list of all attacks
                    attacks_master_list.append(
                        {key: attack_obj[key] for key in SELECTED_ATTACK_KEY if key in attack_obj})

        except KeyError:
            print("No more attacks left to process")
            break
    print(f'Total API calls made -> {count}')
    return attacks_master_list


### GENERATE THE REPORT
def generate_report(hero_faction_name, enemy_faction_name, duration_txt, api_key):
    if api_key is not None:
        masked_api_key = "*****" + api_key[-5:]
        print("Using API Key:", masked_api_key)
    else:
        print("API Key not defined.")

    start_stamp, end_stamp = get_start_time_end_time(duration_txt)
    print(f"start_stamp:{start_stamp} - end_stamp:{end_stamp}")
    # step 1 - call torn api and get a list of all the attacks & received during the RW period OR load from previously written file
    attacks_master_list = load_list()
    if attacks_master_list is None:
        attacks_master_list = fetch_attacks(end_stamp, start_stamp, api_key)
        save_list(attacks_master_list)
    # step 2 - process attacks
    scores = process_attacks(hero_faction_name, enemy_faction_name, attacks_master_list)
    save_summary(scores)


generate_report(
    hero_faction_name="The Power Rangers",
    enemy_faction_name="Drunk Squad",
    duration_txt="15:00:00 - 07/04/23 until 13:03:05 - 08/04/23",
    api_key=API_KEY)
visualize_report()
