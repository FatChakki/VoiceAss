def display_location(location):
    print(location["description"])

def handle_choice(location, choice):
    if choice in location["choices"]:
        outcome = location["choices"][choice]
        print(outcome["description"])
        if "location" in outcome:
            return outcome["location"]
        else:
            return None
    else:
        print("Неправильный выбор!")
        return location

locations = {
    "начало": {
        "description": "Вы находитесь в темном лесу. Перед вами две дороги. Куда вы пойдете?",
        "choices": {
            "лево": {"description": "Вы идете по левой дороге.", "location": "река"},
            "право": {"description": "Вы идете по правой дороге.", "location": "деревня"}
        }
    },
    "река": {
        "description": "Вы подошли к реке. Что будете делать?",
        "choices": {
            "перейти реку": {"description": "Вы переходите реку и находите клад.", "location": None},
            "вернуться": {"description": "Вы возвращаетесь в лес.", "location": "начало"}
        }
    },
    "деревня": {
        "description": "Вы попали в деревню. Что будете делать?",
        "choices": {
            "найти работу": {"description": "Вы нашли работу и стали счастливы.", "location": None},
            "вернуться": {"description": "Вы возвращаетесь в лес.", "location": "начало"}
        }
    }
}

def start_quest():
    current_location = "начало"
    while current_location is not None:
        display_location(locations[current_location])
        choice = input("Выберите действие: ")
        current_location = handle_choice(locations[current_location], choice)