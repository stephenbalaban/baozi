#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import datetime
from decimal import Decimal
import shelve
from contextlib import closing

import web

import localconf

# /analytics
urls = (
            "/?", "Home",
)


app = web.application(urls, globals())
render = web.template.render('templates')

# baozi pricing & db
DB = 'baozi.db'
BAO_PRICE = Decimal('0.70')

# webpy sendmail with gmail
web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
web.config.smtp_username = localconf.email
web.config.smtp_password = localconf.password
web.config.smtp_starttls = True

def get_bao_count(database=DB):
    with closing(shelve.open(database, 'c')) as db:
        if 'count' in db:
            return db['count']
        return 0

def set_bao_count(count, database=DB):
    with closing(shelve.open(database, 'c')) as db:
        db['count'] = count
    return count

class Home:
    def GET(self):
        i = web.input(msg="")
        return render.index(bao_count=get_bao_count(), bao_price=BAO_PRICE, msg=i.msg)

    def POST(self):
        i = web.input(total=0, order=None, name=None, payment="cash")
        order = {}
        if i.order and i.total and i.name and i.payment:
            order = order_bao(total=i.total, order_info=i.order, name=i.name, payment=i.payment)
            return render.order(order=order)
        raise web.seeother("/?msg=fill+in+your+bao+form")

def add_order(value, database=DB):
    timestamp = str(datetime.datetime.utcnow())
    with closing(shelve.open(database, 'c')) as db:
        db[timestamp] = value
    return timestamp

def order_bao(total, order_info, name, payment):
    total = Decimal(str(total)) 
    n = total / BAO_PRICE
    set_bao_count(get_bao_count() + n)
    order = { "name": name,
              "order": order_info,
              "total": total,
              "payment": payment,
              "potential_bao": n }
    timestamp = add_order(order)
    order['placed'] = timestamp

    # send email
    send_bao(name, total, order_info, timestamp, payment)

    return order

def send_bao(name, total, order_info, timestamp, payment="cash", email_from=localconf.email, email_to=localconf.to_email):
    message = """%s, you got a new bao order! 

order:

    for: %s
    order: %s

    payment: %s
    total: %s

    placed: %s

you rock!
""" % (localconf.name, name, order_info, payment, total, timestamp)
    subject = 'a new bao order! %s wants %s, total: $%s (%s)' % (name, order_info, total, payment)
    web.sendmail(email_from, email_to, subject, message)

if __name__ == "__main__":
    app.run()
