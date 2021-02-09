import asyncio
import json
import os
import socket
import threading
import time

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen

from utils import create_logger

logger = None

application = None

listeners = set()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler), (r"/list", ListHandler), (r"/ws", WSHandler), (r"/chat", ChatHandler),]
        settings = dict(
            cookie_secret="secret",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super().__init__(handlers, **settings)
    
    def run(self, port=8080):
        self.listen(port)
        tornado.ioloop.IOLoop.instance().start()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=WSHandler.cache)


class ListHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("list.html")


class ChatHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("room.html")


class WSHandler(tornado.websocket.WebSocketHandler):
    cache = []

    def open(self):
        logger.info("connection opened")
        listeners.add(self)

    def on_message(self, message):
        logger.info(f"Received message: {message}")
        broadcast({
            "type": "message",
            "data": {
                "author": "Vijay",
                "text": f"Server - {message}",
                "color": "blue",
            }
        })
        # parsed = tornado.escape.json_decode(message)

    def on_close(self):
        logger.info("connection closed")
        listeners.remove(self)


def broadcast(message):
    if isinstance(message, bytes):
        message = message.decode('utf-8')
    
    if isinstance(message, str):
        payload = json.dumps({
            "type": "message",
            "data": {
                "author": "Poll",
                "text": f"{message}",
                "color": "green",
            }
        })
    else:
        payload = message
    
    for listener in listeners:
        listener.write_message(payload)


application = Application()


def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run()


def main():
    global logger
    logger = create_logger('websocket')

    event_loop_thread = threading.Thread(target=start_server)
    event_loop_thread.daemon = True
    event_loop_thread.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 8081))
    while True:
        data, addr = s.recvfrom(8192)
        logger.info(f"Received: {data}")
        broadcast(data)
        # tornado.ioloop.IOLoop.instance().add_callback(lambda: broadcast(data))


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)
