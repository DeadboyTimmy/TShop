#
# [!] ничего не надо трогать.
#
from flask import Flask
from threading import Thread
import time
start_time = time.time()
app = Flask('')
@app.route('/')
def main():
    return '1'
def run():
    app.run(host="0.0.0.0", port=8080)
def keep_alive():
    server = Thread(target=run)
    server.start()