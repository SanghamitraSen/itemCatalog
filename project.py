from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


# Connecting to Database and creating database session
engine = create_engine('sqlite:///Catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Creating anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32)
                    )
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validating state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtaining authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrading the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Checking that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submiting request
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # Abort if there was an error in the access token info
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifying that the access token is used for the correct user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifying that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                                json.dumps(
                                           'Current user is already connected.'
                                           ),
                                200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # seeing if user exists,make a new one if doesn't exist
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 200px; height: 200px;border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Route for logout


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Resetting the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        op = '<h1>Successfully logged out</h1>'
        op += '<a href="/login">Click to login</a>'
        op += '<br/>OR<br/>'
        op += '<a href="/">Continue as guest</a>'
        return op
    else:
        # if the given token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category list info
@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[r.serialize for r in categories])

# JSON APIs to view particular category items


@app.route('/category/<int:cid>/list/JSON')
def categoryItemsJSON(cid):
    category = session.query(Category).filter_by(id=cid).one()
    items = session.query(Item).filter_by(
        cid=cid).all()
    return jsonify(Items=[i.serialize for i in items])

# JSON APIs to view particular item's info


@app.route('/category/<int:cid>/list/<int:mid>/JSON')
def categoryItemJSON(cid, mid):
    C_Item = session.query(Item).filter_by(id=mid).one()
    return jsonify(Category_Items=C_Item.serialize)


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

# Edit a category


@app.route('/category/<int:cid>/edit/', methods=['GET', 'POST'])
def editCategory(cid):
    editedCategory = session.query(
        Category).filter_by(id=cid).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCategory.user_id != login_session['user_id']:
        return (
                "<script>function myFunction() "
                "{alert('You are not authorized to edit this');}"
                "</script><body onload='myFunction()''>"
                )
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('ecategory.html', category=editedCategory)


# Delete a category
@app.route('/categories/<int:cid>/delete/', methods=['GET', 'POST'])
def deleteCategory(cid):
    categoryToDelete = session.query(
        Category).filter_by(id=cid).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return (
                "<script>function myFunction() "
                "{alert('You are not authorized to delete this');}"
                "</script><body onload='myFunction()''>"
                )
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', cid=cid))
    else:
        return render_template('dcategory.html', category=categoryToDelete)

# Show a particular category items list


@app.route('/category/<int:cid>/')
@app.route('/category/<int:cid>/items/')
def showItems(cid):
    category = session.query(Category).filter_by(id=cid).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(
        cid=cid).all()
    if ('username' not in login_session or
    creator.id != login_session['user_id']):
        return render_template('publicitemlist.html',
                               items=items, category=category, creator=creator)
    else:
        return render_template('itemlist.html',
                               items=items, category=category, creator=creator)


# Create a new item
@app.route('/category/item/new/', methods=['GET', 'POST'])
def newfromscratch():
    if 'username' not in login_session:
        return redirect('/login')
    user_id = login_session['user_id']
    categories = session.query(Category).all()
    if request.method == 'POST':
        cid = request.form['category']
        addNewItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            cid=request.form['category'],
            user_id=login_session['user_id'])
        session.add(addNewItem)
        session.commit()
        flash("New catalog item created!", 'success')
        return redirect(url_for('showItems', cid=cid))
    else:
        return render_template('newitem.html',
                               categories=categories, user_id=user_id)


# Edit an item
@app.route('/category/<int:cid>/item/<int:mid>/edit', methods=['GET', 'POST'])
def editItem(cid, mid):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=mid).one()
    category = session.query(Category).filter_by(id=cid).one()
    if login_session['user_id'] != category.user_id:
        return (
                "<script>function myFunction() "
                "{alert('You are not authorized to delete this');}"
                "</script><body onload='myFunction()''>"
                )
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItems', cid=cid))
    else:
        return render_template('eitem.html', cid=cid, mid=mid, item=editedItem)


# Delete an item
@app.route('/category/<int:cid>/item/<int:mid>/delete',
           methods=['GET', 'POST'])
def deleteItem(cid, mid):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=cid).one()
    itemToDelete = session.query(Item).filter_by(id=mid).one()
    if login_session['user_id'] != category.user_id:
        return (
            "<script>function myFunction() "
            "{alert('You are not authorized to delete this');}"
            "</script><body onload='myFunction()''>"
            )
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', cid=cid))
    else:
        return render_template('ditem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
