from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response, abort
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from datetime import datetime


views = Blueprint('views', __name__)

# @views.route('/cook')
# def cook():
#  response = make_response('<h1>This document carries a cookie!</h1>')
#  response.status_code
#  return response

@views.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return '<h1>Hello, {}</h1>'.format(user.name)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) <  1:
            flash('You cannot send an empty post', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)



# def new():
#  return '<h1>Hello World!</h1>'
# views.add_url_rule('/new', 'new', new)


# @views.route('/user/<name>')
# def user(name):
#  return '<h1>Hello, {}!</h1>'.format(name)

@views.route('/new')
def index():
 user_agent = request.headers.get('User-Agent')
 return '<p>Your browser is {}</p>'.format(user_agent)


@views.route('/delete-note', methods =['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})



@views.route('/edit/<int:id>/', methods=['POST'])
@login_required
def edit(id):
    article_to_edit = Note.query.get_or_404(id)

    if current_user.username == article_to_edit.user_id:
        if request.method == 'POST':
            article_to_edit.data = request.form.get('data')
            # article_to_edit.content = request.form.get('content')

            db.session.commit()

            flash("Your changes have been saved.")
            return redirect(url_for('edit', id=article_to_edit.id))

        context = {
            'note': article_to_edit
        }

        return render_template('edit.html', **context)

    flash("You cannot edit another user's article.")
    return redirect(url_for('index'))
