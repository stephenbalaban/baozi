#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import web
import datetime

# /analytics
urls = (
            "/?", "Home",
)
app = web.application(urls, globals())

class Home:
    def GET(self):
        return "HELLO! 你好!"

    def POST(self):
        return "No api, yet..."

if __name__ == "__main__":
    app.run()
