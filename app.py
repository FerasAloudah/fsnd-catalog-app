from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask import session as login_session
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import logout_user, current_user, LoginManager
from flask_login import login_required, login_user
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from create_database import Category, Item, OAuth, User
from flask_dance.consumer.backend.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
import os

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
DBSession = sessionmaker(bind=engine)
session = DBSession()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
github_blueprint = make_github_blueprint(
    client_id='dcaab45321e74cf57bba',
    client_secret='d59ca482739be7524a00b22bddd44d28176bd4ab')
app.register_blueprint(github_blueprint, url_prefix='/login')

login_manager = LoginManager(app)
login_session['logged_in'] = False


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))


github_blueprint_backend = SQLAlchemyStorage(OAuth, session, user=current_user)


@app.route('/')
@app.route('/catalog/')
def home():
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.id.desc()).limit(20)
    return render_template('catalog.html', session=session, Category=Category,
                           categories=categories, items=items,
                           title='Catalog', subtitle='Latest Items',
                           logged_in=login_session['logged_in'])


@app.route('/json/')
@app.route('/catalog.json/')
def catalog_json():
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.id.desc())
    return jsonify(category=[category.serialize for category in categories],
                   items=[item.serialize for item in items])


@app.route('/catalog/<path:category_name>.json/')
def category_json(category_name):
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(category=category.serialize,
                   items=[item.serialize for item in items])


@app.route('/catalog/<path:category_name>/<path:item_name>/json/')
def item_json(category_name, item_name):
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    item = session.query(Item).filter(
        func.lower(Item.name) == func.lower(item_name),
        Item.category_id == category.id).one()
    return jsonify(category=category.serialize, items=item.serialize)


@app.route('/catalog/<path:category_name>/items/')
@app.route('/catalog/<path:category_name>/')
def view_category(category_name):
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    categories = session.query(Category)
    items = session.query(Item).filter_by(
        category_id=category.id).order_by(Item.id.desc())
    subtitle = category.name + ' items:'
    return render_template('catalog.html', session=session, Category=Category,
                           categories=categories, items=items,
                           title=category.name, subtitle=subtitle,
                           logged_in=login_session['logged_in'])


@app.route('/catalog/<path:category_name>/<path:item_name>/')
def view_item(category_name, item_name):
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    item = session.query(Item).filter(
        func.lower(Item.name) == func.lower(item_name),
        Item.category_id == category.id).one()
    return render_template('item.html', item=item,
                           category=category, title=item.name,
                           logged_in=login_session['logged_in'])


@app.route('/catalog/<path:category_name>/<path:item_name>/edit/',
           methods=['GET', 'POST'])
@login_required
def edit_item(category_name, item_name):
    categories = session.query(Category)
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    item = session.query(Item).filter(
        func.lower(Item.name) == func.lower(item_name),
        Item.category_id == category.id).one()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        session.add(item)
        session.commit()
        return redirect(url_for('home'))

    return render_template('edit_item.html', categories=categories,
                           category=category, item=item,
                           logged_in=login_session['logged_in'])


@app.route('/catalog/<path:category_name>/<path:item_name>/delete/',
           methods=['GET', 'POST'])
@login_required
def delete_item(category_name, item_name):
    categories = session.query(Category)
    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one()
    item = session.query(Item).filter(func.lower(Item.name) ==
                                      func.lower(item_name),
                                      Item.category_id == category.id).one()

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('home'))

    return render_template('delete_item.html', categories=categories,
                           category=category, item=item,
                           logged_in=login_session['logged_in'])


@app.route('/catalog/add_item/', methods=['GET', 'POST'])
@login_required
def add_item():
    categories = session.query(Category)

    if request.method == 'POST':
        item = request.form['name']
        description = request.form['description']
        category_id = request.form['category']
        session.add(Item(name=item, description=description,
                         category_id=category_id))
        session.commit()
        return redirect(url_for('home'))

    return render_template('add_item.html', categories=categories,
                           logged_in=login_session['logged_in'])


@app.route('/catalog/add_category/', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category = request.form['name']
        session.add(Category(name=category))
        session.commit()
        return redirect(url_for('home'))

    return render_template('add_category.html',
                           logged_in=login_session['logged_in'])


@app.route('/login/')
def login():
    if not github.authorized:
        return redirect(url_for('github.login'))

    login_session['logged_in'] = True
    account_info = github.get('/user')
    account_info_json = account_info.json()
    account_name = account_info_json['login']
    return render_template('login.html', account_name=account_name,
                           logged_in=login_session['logged_in'])


@oauth_authorized.connect_via(github_blueprint)
def logged_in(blueprint, token):
    account_info = blueprint.session.get('/user')
    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['login']

        query = session.query(User).filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username)
            session.add(user)
            session.commit()

        login_user(user)
        login_session['logged_in'] = True


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    login_session['logged_in'] = False
    del app.blueprints['github'].token
    return redirect(url_for('home'))


if __name__ == '__main__':
    login_session['logged_in'] = current_user.is_authenticated
    app.secret_key = 'super_secret_key'
    app.run(host="18.195.199.247.xip.io", port=5000, debug=True)
