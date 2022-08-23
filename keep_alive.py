from flask import Flask
from threading import Thread

''' 
    This keeps the bot running 24/7 and reboots it if it goes offline
'''

app = Flask('')

@app.route('/')
def home():
    return "*this bot is running* message"

def run():
    app.run(host='0.0.0.0', port = 8080)

def keep_alive():
    t = Thread(target = run)
    t.start()