from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import socket
import os
import logging
import signal
import sys

alive_counter = 0


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def start_server(app, host, port, port_max):
    # loop for an open port
    while check_port(host, port):
        port += 1
        if port >= port_max:
            print("No available ports.")
            quit()
        continue
    # we found the port, so let's popen the app
    # with open("port.txt", "w") as file:
    #     file.write(str(port))
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
    return


def exit_if_not_alive(self):
    global alive_counter
    print("checking for alive")
    alive_counter += 10
    if alive_counter >= 10:
        self.shutdown()


def shutdown():
    print("exiting")
    os._exit(0)


def start(connector):
    host = "127.0.0.1"
    port = 5000
    port_max = 40000
    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)
    # scheduler = BackgroundScheduler(daemon=True)
    # scheduler.add_job(exit_if_not_alive, "interval", seconds=10)
    # scheduler.start()

    @app.route("/")
    def show_index():
        content = "i'm in!"
        content += '''
        <br><br><a href="/api/send-prompt">send-prompt </a>
<br><br><a href="/api/send-filepath">send-filepath </a>
<br><br><a href="/api/start-bot">start bot </a>
<br><br><a href="/api/stop-bot">stop bot </a>
<br><br><a href="/api/status">status </a>
<br><br><a href="/api/config-done">config done </a>
<br><br><a href="/api/set-download-dir">set_d_dir </a>
<br><br><a href="/api/get-download-dir">get_d_dir</a>
<br><br><a href="/api/check">check</a>
'''
        return content

    @app.route("/api/send-prompt", methods=["POST", "GET"])
    def send_prompt():
        print(request)
        # data = request.get_json()
        # prompt = data["prompt"]
        prompt = request.args.get('prompt')
        if prompt:
            connector.send_prompt_to_bot(prompt)
        return f"Prompt: {prompt}."

    @app.route("/api/send-filepath", methods=["POST", "GET"])
    def send_filepath():
        print(request)
        # data = request.get_json()
        # file_path = data["filepath"]
        filepath = request.args.get('filepath')
        if filepath:
            connector.send_file_to_bot(filepath)
        return f"Filepath: {filepath}."

    @app.route("/api/start-bot", methods=["POST", "GET"])
    def start_bot():
        print(request)
        return connector.start_bot()

    @app.route("/api/stop-bot", methods=["POST", "GET"])
    def stop_bot():
        print(request)
        return connector.stop_bot()

    @app.route("/api/status", methods=["POST", "GET"])
    def get_status():
        print(request)
        return connector.get_status()

    @app.route("/api/config-done", methods=["POST", "GET"])
    def are_settings_completed():
        print(request)
        return connector.are_settings_completed()

    @app.route("/api/set-download-dir", methods=["POST", "GET"])
    def set_download_dir():
        print(request)
        # data = request.get_json()
        # path = data["path"]
        path = request.args.get('path')
        return connector.send_file_to_bot(path)

    @app.route("/api/get-download-dir", methods=["POST", "GET"])
    def get_download_dir():
        print(request)
        return connector.get_download_dir()

    @app.route("/api/check", methods=["POST", "GET"])
    def check():
        connector.check_bot()
        return ""

    # start the server (must be at the end)
    start_server(app, host, port, port_max)

