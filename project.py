from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Component, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///pccomponents.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/components')
def showComponents():
    components = session.query(Component).order_by(asc(Component.name))
    return render_template('main.html', components=components)


@app.route('/components/<string:component>/')
def showComponentItems(component):
    component_item = session.query(Item)
    return render_template('component-items.html', component_item=component_item)


@app.route('/components/<string:component>/<string:item>')
def showItem(component, item):
    return render_template('item.html')


@app.route('/components/add')
def addItem():
    return render_template('add-item.html')


@app.route('/components/<string:component>/<string:item>/edit')
def editItem(component, item):
    return render_template('edit-item.html')


@app.route('/components/<string:component>/<string:item>/delete')
def deleteItem(component, item):
    return render_template('delete-item.html')


##@app.route('/components.json')
##def showJSON()


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
