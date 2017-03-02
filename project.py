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
    component = session.query(Component).filter_by(name=component).one()
    allItems = session.query(Item).filter_by(component=component).all()

    return render_template('component-items.html', allItems=allItems)


@app.route('/components/<string:component>/<string:item>')
def showItem(component, item):
    item = session.query(Item).filter_by(name=item).one()
    return render_template('item.html', item=item)


@app.route('/components/add', methods=['GET', 'POST'])
def addItem():
    if request.method == 'POST':
        component_name = request.form['component']
        component = session.query(Component).filter_by(name=component_name).one()

        price_item = str(request.form['price'])
        newItem = Item(name=request.form['name'], price=price_item,
                       description=request.form['description'], component=component)
        session.add(newItem)
        session.commit()

        return redirect(url_for('showComponentItems', component=request.form['component']))
    else:
        return render_template('add-item.html')


@app.route('/components/<string:component>/<string:item>/edit', methods=['GET', 'POST'])
def editItem(component, item):

    if request.method == 'POST':
        item = session.query(Item).filter_by(name=item).one()

        component_name = request.form['component']
        component = session.query(Component).filter_by(name=component_name).one()

        print(item.name)
        item.name = request.form['name']
        item.price = str(request.form['price'])
        item.description = request.form['description']
        item.component = component
        session.commit()

        return redirect(url_for('showComponentItems', component=request.form['component']))
    else:
        item = session.query(Item).filter_by(name=item).one()

        return render_template('edit-item.html', item=item)


@app.route('/components/<string:component>/<string:item>/delete', methods=['GET', 'POST'])
def deleteItem(component, item):
    if request.method == 'POST':
        item = session.query(Item).filter_by(name=item).one()

        item_component = item.component.name
        session.delete(item)
        session.commit()

        return redirect(url_for('showComponentItems', component=item_component))
    else:
        item = session.query(Item).filter_by(name=item).one()
        return render_template('delete-item.html', item=item)


@app.route('/components/JSON')
def componentsJSON():
    components = session.query(Component).all()
    return jsonify(components=[c.serialize for c in components])


@app.route('/components/<string:component>/JSON')
def componentItemsJSON(component):
    component = session.query(Component).filter_by(name=component).one()
    items = session.query(Item).filter_by(component=component).all()
    print(items)
    return jsonify(items=[i.serialize for i in items])


@app.route('/components/<string:component>/<string:item>/JSON')
def itemJSON(component, item):
    item = session.query(Item).filter_by(name=item).one()
    return jsonify(item=item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
