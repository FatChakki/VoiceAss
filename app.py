# машинное обучения для реализации возможности угадывания намерений
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
from googlesearch import search  # поиск в Google
from pyowm import OWM  # использование OpenWeatherMap для получения данных о погоде
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from dotenv import load_dotenv  # загрузка информации из .env-файла
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import googletrans  # использование системы Google Translate
import pyttsx3  # синтез речи (Text-To-Speech)
import wikipediaapi  # поиск определений в Wikipedia
import random  # генератор случайных чисел
import webbrowser  # работа с использованием браузера по умолчанию (открывание вкладок с web-страницей)
import traceback  # вывод traceback без остановки работы программы при отлове исключений
import json  # работа с json-файлами и json-строками
import wave  # создание и чтение аудиофайлов формата wav
import os  # работа с файловой системой
import requests
import quest


class Translation:
    """
    Получение вшитого в приложение перевода строк для создания мультиязычного ассистента
    """
    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    with open("script.json", "r", encoding="UTF-8") as file:
        script = json.load(file)

    def get(self, text: str):
        """
        Получение перевода строки из файла на нужный язык (по его коду) и с учетом вариации
        :param text: текст, который требуется перевести
        :return: вшитый в приложение перевод текста
        """
        if text in self.translations:
            return self.translations[text][assistant.mode][assistant.speech_language]
        else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возврат исходного текста
            print(colored("Not translated phrase: {}".format(text), "red"))
            return text
        
    def game(self, text: str):
        """
        """
        print(colored(text, "red"))
        if text in self.script:
            return self.script[text]
        else:
            print(colored("Error", "red"))
            return text


class OwnerPerson:
    """
    Информация о владельце, включающие имя, город проживания, родной язык речи, изучаемый язык (для переводов текста)
    """
    name = ""
    home_city = ""
    native_language = ""
    target_language = ""


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    Примечание: для мультиязычных голосовых ассистентов лучше создать отдельный класс,
    который будет брать перевод из JSON-файла с нужным языком
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""
    mode = ""


def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        ttsEngine.setProperty("voice", voices[0].id)


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # запоминание шумов окружения для последующей очистки звука от них
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            play_voice_assistant_speech(translator.get("Can you check if your microphone is on, please?"))
            traceback.print_exc()
            return

        # использование online-распознавания через Google (высокое качество распознавания)
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language=assistant.recognition_language).lower()

        except speech_recognition.UnknownValueError:
            pass  # play_voice_assistant_speech("What did you say again?")

        # в случае проблем с доступом в Интернет происходит попытка использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print(colored("Trying to use offline recognition...", "cyan"))
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-" + assistant.speech_language + "-0.4"):
            print(colored("Please download the model from:\n"
                          "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.",
                          "red"))
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-" + assistant.speech_language + "-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        traceback.print_exc()
        print(colored("Sorry, speech service is unavailable. Try again later", "red"))

    return recognized_data


def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def play_failure_phrase(*args: tuple):
    """
    Проигрывание случайной фразы при неудачном распознавании
    """
    failure_phrases = [
        translator.get("Can you repeat, please?"),
        translator.get("What did you say again?")
    ]
    play_voice_assistant_speech(failure_phrases[random.randint(0, len(failure_phrases) - 1)])


def play_greetings(*args: tuple):
    """
    Проигрывание случайной приветственной речи
    """
    greetings = [
        translator.get("Hello, {}! How can I help you today?").format(person.name),
        translator.get("Good day to you {}! How can I help you today?").format(person.name)
    ]
    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])



def play_farewell_and_quit(*args: tuple):
    """
    Проигрывание прощательной речи и выход
    """
    farewells = [
        translator.get("Goodbye, {}! Have a nice day!").format(person.name),
        translator.get("See you soon, {}!").format(person.name)
    ]
    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    ttsEngine.stop()
    quit()


def search_for_term_on_google(*args: tuple):
    """
    Поиск в Google с автоматическим открытием ссылок (на список результатов и на сами результаты, если возможно)
    :param args: фраза поискового запроса
    """
    if not args[0]: return
    search_term = " ".join(args[0])

    # открытие ссылки на поисковик в браузере
    url = "https://google.com/search?q=" + search_term
    webbrowser.get().open(url)

    # альтернативный поиск с автоматическим открытием ссылок на результаты (в некоторых случаях может быть небезопасно)
    search_results = []
    try:
        for _ in search(search_term,  # что искать
                        tld="com",  # верхнеуровневый домен
                        lang=assistant.speech_language,  # используется язык, на котором говорит ассистент
                        num=1,  # количество результатов на странице
                        start=0,  # индекс первого извлекаемого результата
                        stop=1,  # индекс последнего извлекаемого результата (я хочу, чтобы открывался первый результат)
                        pause=1.0,  # задержка между HTTP-запросами
                        ):
            search_results.append(_)
            webbrowser.get().open(_)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    print(search_results)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on google").format(search_term))


def search_for_video_on_youtube(*args: tuple):
    """
    Поиск видео на YouTube с автоматическим открытием ссылки на список результатов
    :param args: фраза поискового запроса
    """
    if not args[0]: return
    search_term = " ".join(args[0])
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on youtube").format(search_term))


def search_for_definition_on_wikipedia(*args: tuple):
    """
    Поиск в Wikipedia определения с последующим озвучиванием результатов и открытием ссылок
    :param args: фраза поискового запроса
    """
    if not args[0]: return

    search_term = " ".join(args[0])

    # установка языка (в данном случае используется язык, на котором говорит ассистент)
    wiki = wikipediaapi.Wikipedia('https://meta.wikimedia.org/wiki/User-Agent_policy/ru')

    # поиск страницы по запросу, чтение summary, открытие ссылки на страницу для получения подробной информации
    wiki_page = wiki.page(search_term)
    try:
        if wiki_page.exists():
            play_voice_assistant_speech(translator.get("Here is what I found for {} on Wikipedia").format(search_term))
            webbrowser.get().open(wiki_page.fullurl)

            # чтение ассистентом первых двух предложений summary со страницы Wikipedia
            # (могут быть проблемы с мультиязычностью)
            play_voice_assistant_speech(wiki_page.summary.split(".")[:2])
        else:
            # открытие ссылки на поисковик в браузере в случае, если на Wikipedia не удалось найти ничего по запросу
            play_voice_assistant_speech(translator.get(
                "Can't find {} on Wikipedia. But here is what I found on google").format(search_term))
            url = "https://google.com/search?q=" + search_term
            webbrowser.get().open(url)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return


def get_translation(*args: tuple):
    """
    Получение перевода текста с одного языка на другой (в данном случае с изучаемого на родной язык или обратно)
    :param args: фраза, которую требуется перевести
    """
    if not args[0]: return

    search_term = " ".join(args[0])
    google_translator = googletrans.Translator()
    translation_result = ""

    old_assistant_language = assistant.speech_language
    try:
        # если язык речи ассистента и родной язык пользователя различаются, то перевод выполяется на родной язык
        if assistant.speech_language != person.native_language:
            translation_result = google_translator.translate(search_term,  # что перевести
                                                             src=person.target_language,  # с какого языка
                                                             dest=person.native_language)  # на какой язык

            play_voice_assistant_speech("The translation for {} in Russian is".format(search_term))

            # смена голоса ассистента на родной язык пользователя (чтобы можно было произнести перевод)
            assistant.speech_language = person.native_language
            setup_assistant_voice()

        # если язык речи ассистента и родной язык пользователя одинаковы, то перевод выполяется на изучаемый язык
        else:
            translation_result = google_translator.translate(search_term,  # что перевести
                                                             src=person.native_language,  # с какого языка
                                                             dest=person.target_language)  # на какой язык
            play_voice_assistant_speech("По-английски {} будет как".format(search_term))

            # смена голоса ассистента на изучаемый язык пользователя (чтобы можно было произнести перевод)
            assistant.speech_language = person.target_language
            setup_assistant_voice()

        # произнесение перевода
        play_voice_assistant_speech(translation_result.text)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()

    finally:
        # возвращение преждних настроек голоса помощника
        assistant.speech_language = old_assistant_language
        setup_assistant_voice()


def get_weather_forecast(*args: tuple):
    """
    Получение и озвучивание прогнза погоды
    :param args: город, по которому должен выполняться запос
    """
    # в случае наличия дополнительного аргумента - запрос погоды происходит по нему,
    # иначе - используется город, заданный в настройках
    city_name = person.home_city

    if args:
        if args[0]:
            city_name = args[0][0]

    weather_api_key = '5c7457efdfb0f612a8c1280034f1eef2'
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}&units=metric&lang={assistant.speech_language}'
    try:
        # использование API-ключа, помещённого в .env-файл по примеру WEATHER_API_KEY = "01234abcd....."
        response = requests.get(weather_url)
        weather_data = response.json()

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    description = weather_data['weather'][0]['description']
    temperature = int(weather_data['main']['temp'])
    humidity = weather_data['main']['humidity']
    pressure = int(weather_data['main']['pressure'] / 1.333)
    wind_speed = weather_data['wind']['speed']
    # вывод логов
    print(colored("Weather in " + city_name +
                  ":\n * Status: " + description +
                  "\n * Wind speed (m/sec): " + str(wind_speed) +
                  "\n * Temperature (Celsius): " + str(temperature) +
                  "\n * Humidity (%): " + str(humidity) +
                  "\n * Pressure (mm Hg): " + str(pressure), "yellow"))

    # озвучивание текущего состояния погоды ассистентом (здесь для мультиязычности требуется дополнительная работа)
    play_voice_assistant_speech(translator.get("It is {0} in {1}").format(description, city_name))
    play_voice_assistant_speech(translator.get("The temperature is {} degrees Celsius").format(str(temperature)))
    play_voice_assistant_speech(translator.get("The humidity is {} percent").format(str(humidity)))
    play_voice_assistant_speech(translator.get("The wind speed is {} meters per second").format(str(wind_speed)))
    play_voice_assistant_speech(translator.get("The pressure is {} mm Hg").format(str(pressure)))


def change_language(*args: tuple):
    """
    Изменение языка голосового ассистента (языка распознавания речи)
    """
    assistant.speech_language = "ru" if assistant.speech_language == "en" else "en"
    setup_assistant_voice()
    print(colored("Language switched to " + assistant.speech_language, "cyan"))


def run_person_through_social_nets_databases(*args: tuple):
    """
    Поиск человека по базе данных социальных сетей ВКонтакте и Facebook
    :param args: имя, фамилия TODO город
    """
    if not args[0]: return

    google_search_term = " ".join(args[0])
    vk_search_term = "_".join(args[0])
    fb_search_term = "-".join(args[0])

    # открытие ссылки на поисковик в браузере
    url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
    webbrowser.get().open(url)

    url = "https://google.com/search?q=" + google_search_term + " site: facebook.com"
    webbrowser.get().open(url)

    # открытие ссылкок на поисковики социальных сетей в браузере
    vk_url = "https://vk.com/people/" + vk_search_term
    webbrowser.get().open(vk_url)

    fb_url = "https://www.facebook.com/public/" + fb_search_term
    webbrowser.get().open(fb_url)

    play_voice_assistant_speech(translator.get("Here is what I found for {} on social nets").format(google_search_term))


def open_apps(*args: tuple):
    """
    """
    openning = " ".join(args[0])

    if openning == 'код':
        os.startfile(r"D:\\Programs\\Microsoft VS Code\\Code.exe")
        play_voice_assistant_speech(translator.get("I open VS Code"))
    elif openning == 'youtube':
        webbrowser.get().open("https://www.youtube.com")
        play_voice_assistant_speech(translator.get("I open Youtube"))
    elif openning == 'steam':
        os.startfile(r"D:\\Programs\\steam\\steam.exe")
        play_voice_assistant_speech(translator.get("I open Steam"))
    else:
        play_voice_assistant_speech('Ебу дал что-ли')


def quest_game():
    """
    """
    play_voice_assistant_speech(translator.get("Start quest"))
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
            return handle_choice(location, input("Выберите действие: "))

    current_location = "начало"
    while current_location != "None":
        display_location(translator.game(current_location))
        choice = input("Выберите действие: ")
        current_location = handle_choice(translator.game(current_location), choice)
    play_voice_assistant_speech(translator.get("It's over"))


# перечень команд для использования в виде JSON-объекта
config = {
    "intents": {
        "greeting": {
            "examples": ["привет", "здравствуй", "добрый день",
                         "hello", "good morning"],
            "responses": play_greetings
        },
        "farewell": {
            "examples": ["пока", "до свидания", "увидимся", "до встречи",
                         "goodbye", "bye", "see you soon"],
            "responses": play_farewell_and_quit
        },
        "google_search": {
            "examples": ["найди в гугл",
                         "search on google", "google", "find on google"],
            "responses": search_for_term_on_google
        },
        "youtube_search": {
            "examples": ["найди видео", "покажи видео",
                         "find video", "find on youtube", "search on youtube"],
            "responses": search_for_video_on_youtube
        },
        "wikipedia_search": {
            "examples": ["найди определение", "найди на википедии",
                         "find on wikipedia", "find definition", "tell about"],
            "responses": search_for_definition_on_wikipedia
        },
        "person_search": {#хуйня бесполезная
            "examples": ["пробей имя", "найди человека",
                         "find on facebook", " find person", "run person", "search for person"],
            "responses": run_person_through_social_nets_databases
        },
        "weather_forecast": {
            "examples": ["прогноз погоды", "какая погода",
                         "weather forecast", "report weather"],
            "responses": get_weather_forecast
        },
        "translation": {#хз мусор
            "examples": ["выполни перевод", "переведи", "найди перевод",
                         "translate", "find translation"],
            "responses": get_translation
        },
        "language": {
            "examples": ["смени язык", "поменяй язык",
                         "change speech language", "language"],
            "responses": change_language
        },
        "open_apps": {
            "examples": ["геннадий", "пиздец", "запускай",
                         "bro"],
            "responses": open_apps
        },
        "quest": {
            "examples": ["квест", "игра", "дай поиграть"
                         "quest"],
            "responses": quest_game
        }
    },

    "failure_phrases": play_failure_phrase
}


def prepare_corpus():
    """
    Подготовка модели для угадывания намерения пользователя
    """
    corpus = []
    target_vector = []
    for intent_name, intent_data in config["intents"].items():
        for example in intent_data["examples"]:
            corpus.append(example)
            target_vector.append(intent_name)

    training_vector = vectorizer.fit_transform(corpus)
    classifier_probability.fit(training_vector, target_vector)
    classifier.fit(training_vector, target_vector)


def get_intent(request):
    """
    Получение наиболее вероятного намерения в зависимости от запроса пользователя
    :param request: запрос пользователя
    :return: наиболее вероятное намерение
    """
    best_intent = classifier.predict(vectorizer.transform([request]))[0]

    index_of_best_intent = list(classifier_probability.classes_).index(best_intent)
    probabilities = classifier_probability.predict_proba(vectorizer.transform([request]))[0]

    best_intent_probability = probabilities[index_of_best_intent]

    # при добавлении новых намерений стоит уменьшать этот показатель
    print(best_intent_probability)
    if best_intent_probability > 0.157:
        return best_intent


def make_preparations():
    """
    Подготовка глобальных переменных к запуску приложения
    """
    global recognizer, microphone, ttsEngine, person, assistant, translator, vectorizer, classifier_probability, classifier

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # настройка данных пользователя
    person = OwnerPerson()
    person.name = "Tanya"
    person.home_city = "Kaluga"
    person.native_language = "ru"
    person.target_language = "en"

    # настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = "Alice"
    assistant.sex = "female"
    assistant.speech_language = "ru"
    assistant.mode = "evil"

    # установка голоса по умолчанию
    setup_assistant_voice()

    # добавление возможностей перевода фраз (из заготовленного файла)
    translator = Translation()

    # загрузка информации из .env-файла (там лежит API-ключ для OpenWeatherMap)
    load_dotenv()

    # подготовка корпуса для распознавания запросов пользователя с некоторой вероятностью (поиск похожих)
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_corpus()


if __name__ == "__main__":
    make_preparations()

    while True:
        # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
        voice_input = record_and_recognize_audio()

        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")

        print(colored(voice_input, "blue"))

        # отделение комманд от дополнительной информации (аргументов)
        if voice_input:
            voice_input_parts = voice_input.split(" ")

            # если было сказано одно слово - выполняем команду сразу без дополнительных аргументов
            if len(voice_input_parts) == 1:
                intent = get_intent(voice_input)
                if intent:
                    config["intents"][intent]["responses"]()
                else:
                    config["failure_phrases"]()

            # в случае длинной фразы - выполняется поиск ключевой фразы и аргументов через каждое слово,
            # пока не будет найдено совпадение
            if len(voice_input_parts) > 1:
                for guess in range(len(voice_input_parts)):
                    intent = get_intent((" ".join(voice_input_parts[0:guess])).strip())
                    print(intent)
                    if intent:
                        command_options = [voice_input_parts[guess:len(voice_input_parts)]]
                        print(command_options)
                        config["intents"][intent]["responses"](*command_options)
                        break
                    if not intent and guess == len(voice_input_parts)-1:
                        config["failure_phrases"]()

# TODO food order
# TODO recommend film by rating/genre (use recommendation system project)
#  как насчёт "название фильма"? Вот его описание:.....