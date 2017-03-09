# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
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

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'pc-components-catalog'

# Connect to Database and create database session

engine = create_engine('sqlite:///pccomponents.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Static pages
@app.route('/')
@app.route('/components')
def showComponents():
    """ Main page show component list """

    username = login_session.get('username')
    picture = login_session.get('picture')
    user_email = login_session.get('email')
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    components = session.query(Component).order_by(asc(Component.name))
    return render_template('main.html', components=components,
                           username=username, picture=picture,
                           STATE=state)


@app.route('/components/<string:component>/')
def showComponentItems(component):
    """ Show items inside a component """

    component = session.query(Component).filter_by(name=component).one()
    allItems = session.query(Item).filter_by(component=component).all()
    username = login_session.get('username')
    picture = login_session.get('picture')
    user_email = login_session.get('email')

    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'component-items.html',
        allItems=allItems,
        component=component,
        username=username,
        picture=picture,
        STATE=state,
        )


@app.route('/components/<string:component>/<string:item>')
def showItem(component, item):
    item = session.query(Item).filter_by(name=item).one()

    username = login_session.get('username')
    picture = login_session.get('picture')
    user_email = login_session.get('email')

    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('item.html', item=item, username=username,
                           picture=picture, STATE=state)


@app.route('/components/add', methods=['GET', 'POST'])
def addItem():
    username = login_session.get('username')

    if username:
        if request.method == 'POST':
            component_name = request.form['component']
            component = \
                session.query(Component).filter_by(name=component_name).one()
            user_email = login_session.get('email')

            price_item = str(request.form['price'])
            newItem = Item(name=request.form['name'], price=price_item,
                           description=request.form['description'],
                           component=component, email=user_email)
            session.add(newItem)
            session.commit()

            return redirect(url_for('showComponentItems',
                            component=request.form['component']))
        else:
            username = login_session.get('username')
            picture = login_session.get('picture')
            user_email = login_session.get('email')

            state = ''.join(random.choice(string.ascii_uppercase
                            + string.digits) for x in xrange(32))
            login_session['state'] = state
            return render_template('add-item.html', username=username,
                                   picture=picture, STATE=state)
    else:
        return redirect(url_for('showComponents'))


@app.route('/components/<string:component>/<string:item>/edit',
           methods=['GET', 'POST'])
def editItem(component, item):
    user_email = login_session.get('email')
    item = session.query(Item).filter_by(name=item).one()
    if user_email == item.email:
        if request.method == 'POST':
            component_name = request.form['component']
            component = \
                session.query(Component).filter_by(name=component_name).one()

            item.name = request.form['name']
            item.price = str(request.form['price'])
            item.description = request.form['description']
            item.component = component
            session.commit()

            return redirect(url_for('showComponentItems',
                            component=request.form['component']))
        else:
            username = login_session.get('username')
            picture = login_session.get('picture')
            user_email = login_session.get('email')

            state = ''.join(random.choice(string.ascii_uppercase
                            + string.digits) for x in xrange(32))
            login_session['state'] = state

            components = session.query(Component).all()
            componentList = []
            for c in components:
                componentList.append(c.name)

            print componentList
            return render_template(
                'edit-item.html',
                item=item,
                componentList=componentList,
                username=username,
                picture=picture,
                STATE=state,
                )
    else:
        return redirect(url_for('showComponents'))


@app.route('/components/<string:component>/<string:item>/delete',
           methods=['GET', 'POST'])
def deleteItem(component, item):
    """ Delete method for a specific item """

    user_email = login_session.get('email')
    item = session.query(Item).filter_by(name=item).one()
    if user_email == item.email:
        if request.method == 'POST':
            item_component = item.component.name
            session.delete(item)
            session.commit()

            return redirect(url_for('showComponentItems',
                            component=item_component))
        else:
            username = login_session.get('username')
            picture = login_session.get('picture')
            user_email = login_session.get('email')

            state = ''.join(random.choice(string.ascii_uppercase
                            + string.digits) for x in xrange(32))
            login_session['state'] = state
            return render_template('delete-item.html', item=item,
                                   username=username, picture=picture,
                                   STATE=state)
    else:
        return redirect(url_for('showComponents'))


@app.route('/components/JSON')
def componentsJSON():
    """ Returns JSON version of the components """

    components = session.query(Component).all()
    return jsonify(components=[c.serialize for c in components])


@app.route('/components/<string:component>/JSON')
def componentItemsJSON(component):
    """ Returns JSON version of the items inside a component """
    component = session.query(Component).filter_by(name=component).one()
    items = session.query(Item).filter_by(component=component).all()
    print items
    return jsonify(items=[i.serialize for i in items])


@app.route('/components/<string:component>/<string:item>/JSON')
def itemJSON(component, item):
    """ Returns JSON version of a specific item """

    item = session.query(Item).filter_by(name=item).one()
    return jsonify(item=item.serialize)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Login with google method. Return error if it's occurred or
        success output """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token doesn't match user."), 401)

        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token client doesn't match."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<div class="output-login">Welcome, '
    output += login_session['username']
    output += '!</div>'
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ Disconnect method deleting user login_session dictionary"""
    # Only disconnect a connect user

    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showComponents'))
    else:

        # For whatever reason, the given token was invalid.

        response = make_response(json.dumps('Failed to revoke token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'Mzs8a3xPMY-BlK-3kEYFslJT'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
