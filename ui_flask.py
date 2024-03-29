from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import socket
import os
import logging
import signal
import sys

alive_counter = 0
methods = ["POST", "GET"]


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def start_server(app, host, port):
    app.run(host=host, port=port, debug=True, use_reloader=False, threaded=True)
    return


def exit_if_not_alive():
    global alive_counter
    alive_counter += 1
    if alive_counter >= 10:
        shutdown()


def shutdown():
    pass
    print("exiting, brutal shutdown")
    os._exit(0)


def start(connector, port=5000):
    host = "127.0.0.1"
    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(exit_if_not_alive, "interval", seconds=1)
    scheduler.start()

    @app.route("/")
    def show_index():
        content = "flask server up"
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

    @app.route("/api/send-prompt", methods=methods)
    def send_prompt():
        data = request.get_json()
        prompt = data["prompt"]
        if prompt:
            connector.send_prompt_to_bot(prompt)
        return f"Prompt: {prompt}."

    @app.route("/api/send-filepath", methods=methods)
    def send_filepath():
        data = request.get_json()
        filepath = data["filepath"]
        suffix = data["suffix"] or ""
        if filepath:
            connector.send_file_to_bot(filepath, suffix)
        return f"Filepath: {filepath}. Suffix: {suffix}."

    @app.route("/api/start-bot", methods=methods)
    def start_bot():
        return connector.start_bot()

    @app.route("/api/stop-bot", methods=methods)
    def stop_bot():
        return connector.stop_bot()

    @app.route("/api/status", methods=methods)
    def get_status():
        keep_alive()
        return connector.get_status()

    @app.route("/api/keep-alive", methods=methods)
    def keep_alive():
        global alive_counter
        alive_counter = 0

    @app.route("/api/config-done", methods=methods)
    def are_settings_completed():
        return connector.are_settings_completed()

    @app.route("/api/set-download-dir", methods=methods)
    def set_download_dir():
        data = request.get_json()
        path = data["path"]
        return connector.set_download_dir(path)

    @app.route("/api/get-download-dir", methods=methods)
    def get_download_dir():
        return connector.get_download_dir()

    @app.route("/api/check", methods=methods)
    def check():
        return connector.check_bot()
    
    @app.route("/api/write-settings", methods=methods)
    def write_settings():
        data = request.get_json()
        return connector.write_settings(data)

    @app.route("/api/read-settings", methods=methods)
    def read_settings():
        response = connector.read_settings()
        return jsonify({"result": response})

    # start the server (must be at the end)
    start_server(app, host, port)

