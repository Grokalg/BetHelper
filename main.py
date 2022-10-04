import time
import requests
import json
from telegram import send_telegram


def send_info_message(current_bet):
    league, first_team, second_team, total, total_high, total_low = current_bet.values()
    message = f'\u26A0\u26A0\u26A0\u26A0\u26A0\u26A0\u26A0\nПора делать ставку TM {total}\n{league}\n{first_team} - {second_team}\nКоэффициент TM - {total_low}\nКоэффициент TБ - {total_high}'
    send_telegram(message)
    # print(message)
    # print("=====================================")

def send_result_message(ischod, ischod_team):
    team_1, team_2 = ischod_team.values()
    if ischod == "win":
        message = f'\u2705\u2705\u2705\u2705\u2705\u2705\u2705\nСтавка выйграла\nМатч между командами:\n{team_1} - {team_2}'
    else:
        message = f'\u274c\u274c\u274c\u274c\u274c\u274c\u274c\nСтавка проиграла\nМатч между командами:\n{team_1} - {team_2}'
    send_telegram(message)
    # print(message)

def get_bets(id_of_bets):
    params = {
        'id': id_of_bets,
        'lng': 'ru',
        'cfview': '0',
        'isSubGames': 'true',
        'GroupEvents': 'true',
        'allEventsGroupSubGames': 'true',
        'countevents': '250',
        'partner': '51',
        'grMode': '2',
        'marketType': '1',
        'isNewBuilder': 'true',
    }

    response = requests.get('https://1xstavka.ru/LiveFeed/GetGameZip', params=params)
    game_result = response.json()
    current_bet = {}
    for bets in game_result["Value"]["GE"]:
        for bet in bets["E"]:
            for item in bet:
                if item["G"] == 4 and item["P"] == 0.5:
                    if item["T"] == 9:
                        current_bet["league"] = game_result["Value"]["L"]
                        current_bet["first_team"] = game_result["Value"]["O1"]
                        current_bet["second_team"] = game_result["Value"]["O2"]
                        current_bet["total"] = item["P"]
                        current_bet["total_high"] = item["C"]
                    if item["T"] == 10:
                        current_bet["total_low"] = item["C"]
    # print(current_bet)
    send_info_message(current_bet)

def get_game(json_file):
    with open(json_file) as json_file:
        data = json.load(json_file)
        for game in data["Value"]:
            game_id = game['I']
            params = {
                'id': game_id,
                'lng': 'ru',
                'cfview': '0',
                'isSubGames': 'true',
                'GroupEvents': 'true',
                'allEventsGroupSubGames': 'true',
                'countevents': '250',
                'partner': '51',
                'grMode': '2',
                'marketType': '1',
                'isNewBuilder': 'true',
            }

            response = requests.get('https://1xstavka.ru/LiveFeed/GetGameZip', params=params)
            game_result = response.json()
            if "TS" in game_result["Value"]["SC"] and "CP" in game_result["Value"]["SC"]:
                if game_result["Value"]["SC"]["TS"] >= 1620 and game_result["Value"]["SC"]["CP"] == 1:
                    if not game_result["Value"]["SC"]["FS"]:
                        for id in game_result["Value"]["SG"]:
                            id_of_bet = id["I"]
                            break
                        with open("db.txt", 'r') as file:
                            t = 0
                            for item in file.readlines():
                                line = item.strip()
                                if line == str(game_id):
                                    t += 1
                            if t == 0:
                                get_bets(id_of_bet)
                                with open('db.txt', 'a') as f:
                                     f.write(f'\n{game_id}')

                if game_result["Value"]["SC"]["TS"] >= 2700 and game_result["Value"]["SC"]["CPS"] == 'Перерыв':
                    with open('db.txt', 'r') as file:
                        for item in file.readlines():
                            line = item.strip()
                            if line == str(game_id):
                                ischod_team = {}
                                ischod_team['team_1'] = game_result["Value"]["O1"]
                                ischod_team['team_2'] = game_result["Value"]["O2"]
                                if not game_result["Value"]["SC"]["FS"]:
                                    ischod = "win"
                                else:
                                    ischod = "lose"
                                with open("db2.txt", 'r') as f:
                                    t = 0
                                    for item in f.readlines():
                                        line = item.strip()
                                        if line == str(game_id):
                                            t += 1
                                    if t == 0:
                                        send_result_message(ischod, ischod_team)
                                        with open('db2.txt', 'a') as f:
                                            f.write(f'\n{game_id}')
                                with open("db.txt", "r") as file:
                                    lines = file.readlines()
                                with open("db.txt", 'w') as file:
                                    for line in lines:
                                        if line != f'{game_id}':
                                            file.write(line)

                if game_result["Value"]["SC"]["TS"] >= 5300:
                    with open("db2.txt", "r") as file:
                        lines = file.readlines()
                    with open("db2.txt", 'w') as file:
                        for line in lines:
                            if line != f'{game_id}':
                                file.write(line)

def main():
    url = 'https://1xstavka.ru/live/football/'
    sport = url.split('/')[-2]
    if sport == 'football':
        sport = str(1)

    params = {
        'sports': sport,
        'count': '10',
        'antisports': '188',
        'partner': '51',
        'getEmpty': 'true',
        'mode': '4',
        'country': '1',
    }

    response = requests.get('https://1xstavka.ru/LiveFeed/BestGamesExtVZip', params=params)
    result = response.json()
    with open('result.json', "w") as file:
        json.dump(result, file)
    get_game('result.json')

if __name__ == '__main__':
    while True:
        main()
        time.sleep(120)

