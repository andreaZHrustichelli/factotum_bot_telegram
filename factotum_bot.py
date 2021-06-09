    import telepot
    from telepot.loop import MessageLoop
    from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

    from pprint import pprint
    import time
    import sys
    import datetime
    import json

    from io import BytesIO

    from pyzbar.pyzbar import decode
    from PIL import Image
    import urllib.request
    from urllib.request import urlopen

    from pydub import AudioSegment

    import speech_recognition as sr

    TOKEN="0000000000000000000000000000000" #da sostituire

    HOT_WORD1=["pippo","Pippo","PIPPO"]
    HOT_WORD2=["pluto","Pluto","PLUTO"]
    HOT_WORD3=["paperino","Paperino","PAPERINO"]

    QRCODE1="qrcode1"
    QRCODE2="qrcode2"
    QRCODE3="qrcode3"

    """
    === TROVA_POSIZIONE ===
    Funzione per scrivere i dati sulla posizione che viene passata al Bot
    tramite l'interrogazione di un web service
    =======================
    """
    def trova_posizione(bot, chat_id, msg):
        bot.sendMessage(chat_id,'Mi hai passato la posizione geografica')
        print(msg["from"] ["first_name"])
        gps_lat=msg["location"] ["latitude"]
        gps_lon=msg["location"] ["longitude"]
        gps_url="http://www.geoplugin.net/extras/nearby.gp?lat=" + str(gps_lat) + "&lon=" + str(gps_lon) + "&format=json"
        with urlopen(gps_url) as response:
          html_response = response.read()
          encoding = response.headers.get_content_charset('utf-8')
          decoded_html = html_response.decode(encoding)

        data_json=json.loads(decoded_html)
        for posti in data_json:
            print(posti["geoplugin_place"], posti["geoplugin_distanceKilometers"], posti["geoplugin_directionHeading"])
            bot.sendMessage(chat_id, "Ti trovi a " + str(posti["geoplugin_distanceKilometers"]) + " Km da " + str(posti["geoplugin_place"]) + " in direzione " + str(posti["geoplugin_directionHeading"]))
        return

    """
    === ANALIZZA_AUDIO ===
    Funzione per convertire in WAV il file audio registrato
    in Telegram (nativo in formato OGG) e analizzare il messaggio audio
    contenuto nel file WAV
    ======================
    """
    def analizza_audio(bot, chat_id, msg):
        print("Funzione ANALIZZA_AUDIO: START")
        ogg_file_id=msg["voice"] ["file_id"]
        print("Funzione ANALIZZA_AUDIO:",ogg_file_id)
        print("Funzione ANALIZZA_AUDIO: Downloading file in formato OGG...")
        bot.download_file(ogg_file_id, "audio_da_telegram.ogg")
        print("Funzione ANALIZZA_AUDIO: Salvataggio file OGG terminato.")
        file_ogg = AudioSegment.from_ogg("audio_da_telegram.ogg")
        file_handle = file_ogg.export("output.wav", format="wav")
        print("Funzione ANALIZZA_AUDIO: Convesione file WAV terminato.")

        r = sr.Recognizer()
        with sr.WavFile("output.wav") as source:
            audio = r.record(source)

        try:
            domanda=r.recognize_google(audio,language="it_IT")
            print("Trascrizione del file audio: " + domanda)   # recognize speech using Google Speech Recognition
            formula_risposta(bot,chat_id,msg,domanda)
        except LookupError:                                 # speech is unintelligible
            print("Impossibile riconoscere del testo nel file audio analizzato")

        return

    """
    === FORMULA_RISPOSTA ===
    Funzione per analizzare il testo digitato dall'utente nella chat
    e formulare la risposta più appropriata sulla base delle 3 HOT_WORD definite
    a livello di programma
    ========================
    """
    def formula_risposta(bot, chat_id, msg, domanda):
        print("Funzione FORMULA_RISPOSTA: START")
        print("Funzione FORMULA_RISPOSTA: La domanda è ",domanda)

        parole=domanda.split(" ")
        parole_chiave=[]
        risposta=""
        for i in parole:
          if i in HOT_WORD1:
              parole_chiave.append(i)
              bot.sendMessage(chat_id,"Trovata la HOT_WORD1")
          if i in HOT_WORD2:
              parole_chiave.append(i)
              bot.sendMessage(chat_id,"Trovata la HOT_WORD2")
              #bot.sendDocument(chat_id, open('file_name.pdf', 'rb'))
          if i in HOT_WORD3:
              parole_chiave.append(i)
              bot.sendMessage(chat_id,"Trovata la HOT_WORD3")
              #bot.sendMessage(chat_id, "https://www.google.it")

        if len(parole_chiave)==0:
          bot.sendMessage(chat_id,"Spiacente, non sono riuscito a individuare la richiesta.")
        return

    """
    === LEGGI_QR_CODE ===
    Funzione per analizzare l'immagine passata al BOT nella chat
    e cerca se il testo presente nel QR code coincide con il testo
    definito nelle 3 variabili di programma con lo scopo di
    effettuare delle scelte sulla base del contenuto del QR code.
    =====================
    """
    def leggi_QR_code(bot,chat_id,msg):
        bot.sendMessage(chat_id, 'Ricerca dei QR Code in corso...')
        raw_img = BytesIO()
        bot.download_file(msg['photo'][-1]['file_id'], raw_img)
        img = Image.open(raw_img)
        qrcodes = decode(img)

        if len(qrcodes) > 0:
            for code in qrcodes:
                print("Il contenuto del QR code è:", qrcodes)
                qr_string=str(code.data)
                qr_string_unicode=qr_string[2:-1]

                bot.sendMessage(chat_id, "Il QRCode contiene il testo: " + qr_string_unicode)
                if qr_string_unicode==QRCODE1:
                    bot.sendMessage(chat_id, "Trovato il QRCODE1")
                elif qr_string_unicode==QRCODE2:
                    bot.sendMessage(chat_id, "Trovato il QRCODE2")
                elif qr_string_unicode==QRCODE3:
                    bot.sendMessage(chat_id, "Trovato il QRCODE3")

        else:
            bot.sendMessage(chat_id, "Non ho trovato QRCode nella foto...")
        return

    """
    === ATTIVA MAGGIORDOMO ===
    Funzione attivare l'Inline Keyboard presente in Telegram.
    L'InlineKeyboard visualizza 3 pulsanti
    Il pulsante key1 visualizza un sottomenù con altri 2 pulsanti e quello per tornare indietro
    Il pulsante key2 visualizza un elenco di anni e il pulsante per tornare indietro
    Il pulsante key3 visualizza direttamente un testo
    Questa è la funzione base. Ci sono altre funzioni per gestire le risposte dell'utente.
    ==========================
    """
    def attiva_maggiordomo(chat_id):
        print("Maggiordomo attivato")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [InlineKeyboardButton(text='Testo key1', callback_data='key1'),
                          InlineKeyboardButton(text='Testo key2', callback_data='key2'),
                          InlineKeyboardButton(text='Testo key3', callback_data='key3')]
                     ])
        bot.sendMessage(chat_id,"Attivazione del Maggiodomo in corso...",reply_markup=keyboard)

    def attiva_maggiordomo_key1(chat_id):
        print("Maggiordomo KEY1 attivato")
        key1_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [InlineKeyboardButton(text='Testo key1 sub 1', callback_data='key1_1'),
                         InlineKeyboardButton(text='Testo key1 sub 2', callback_data='key1_2')],
                         [InlineKeyboardButton(text='Torna indietro', callback_data='from_key1_back')]
                     ])
        bot.sendMessage(chat_id, "Entro nella sezione KEY1...",reply_markup=key1_keyboard)

    def attiva_maggiordomo_key2(chat_id):
        print("Maggiordomo KEY2 attivato")
        key2_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [InlineKeyboardButton(text='2016', callback_data='2016')],
                         [InlineKeyboardButton(text='2017', callback_data='2017')],
                         [InlineKeyboardButton(text='2018', callback_data='2018')],
                         [InlineKeyboardButton(text='Torna indietro', callback_data='from_key2_back')]
                     ])
        bot.sendMessage(chat_id, "Entro nella sezione KEY2...",reply_markup=key2_keyboard)

    def attiva_maggiordomo_key3(chat_id):
        print("Maggiordomo KEY3 attivato")
        bot.sendMessage(chat_id, "Entro nella sezione KEY3...")

    def on_chat_message(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if content_type=='location':
            print("Hai inserito la tua posizione")
            print(msg)
            trova_posizione(bot,chat_id, msg)

        if content_type=='photo':
            print("Hai caricato una immagine")
            print(msg)
            leggi_QR_code(bot,chat_id,msg)

        if content_type=='voice':
            print("Ho ricevuto un messaggio audio")
            print(msg)
            analizza_audio(bot,chat_id,msg)

        if content_type == 'text':
             text = msg['text']
             if text == '/start':
                 bot.sendMessage(chat_id,"Benvenuto... "+ msg["from"]['first_name']+" hai attivato il bot Factotum!")
             elif text == '/info':
                 bot.sendMessage(chat_id,"Hai attivato il comando per visualizzare le info sul bot Factotum")
             elif text == '/ambrogio':
                attiva_maggiordomo(chat_id)
             else:
                formula_risposta(bot, chat_id, msg,text)


    def on_callback_query(msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, chat_id, query_data)
        if query_data=="key1":
            attiva_maggiordomo_key1(chat_id)
        elif query_data=="key2":
            attiva_maggiordomo_key2(chat_id)
        elif query_data=="key3":
            attiva_maggiordomo_key3(chat_id)
        elif query_data == 'from_key1_back':
            attiva_maggiordomo(chat_id)
        elif query_data == 'from_key2_back':
            attiva_maggiordomo(chat_id)
        elif query_data == 'from_key3_back':
            attiva_maggiordomo(chat_id)
        elif query_data == '2016':
            bot.sendMessage(chat_id, "Hai scelto l'anno 2016")
        elif query_data == '2017':
            bot.sendMessage(chat_id, "Hai scelto l'anno 2017")
        elif query_data == '2018':
            bot.sendMessage(chat_id, "Hai scelto l'anno 2018")
        elif query_data == 'key1_1':
            bot.sendMessage(chat_id, "Hai premuto il tasto KEY1_1")
        elif query_data == 'key1_2':
            bot.sendMessage(chat_id, "Hai premuto il tasto KEY1_2")
        elif query_data == 'key2_1':
            bot.sendMessage(chat_id, "Hai premuto il tasto KEY2_1")
        elif query_data == 'key2_2':
            bot.sendMessage(chat_id, "Hai premuto il tasto KEY2_2")


    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Listening ...')


    while 1:
        time.sleep(10)
