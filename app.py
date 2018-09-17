# from datetime import datetime
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class TinyWebDB(db.Model):
    __tablename__ = 'tinywebdb'
    tag = db.Column(db.String, primary_key=True, nullable=False)
    value = db.Column(db.String, nullable=False)
    # The 'date' column is needed for deleting older entries, so not really required
    # date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


db.create_all()
db.session.commit()


@app.route('/')
def hello_world():
    return 'Hello, I\'m UP and RUNNING !'


@app.route('/storeavalue', methods=['POST'])
def store_a_value():
    tag = request.form['tag']
    value = request.form['value']
    if tag:
        # Prevent Duplicate Key error by updating the existing tag
        existing_tag = TinyWebDB.query.filter_by(tag=tag).first()

        # If value is empty, then delete entry
        if existing_tag and value == 'entrytodelete':
            db.session.remove(existing_tag)
            db.session.commit()
        elif existing_tag:
            existing_tag.value = value
            db.session.commit()
        else:
            data = TinyWebDB(tag=tag, value=value)
            db.session.add(data)
            db.session.commit()
        return jsonify(['STORED', tag, value])
    return 'Invalid Tag!'


@app.route('/getvalue', methods=['POST'])
def get_value():
    tag = request.form['tag']
    if tag:
        value = TinyWebDB.query.filter_by(tag=tag).first().value
        return jsonify(['VALUE', tag, value])
    return 'Invalid Tag!'

@app.route('/getscores/actionable/user/<user>', methods=['GET', 'POST'])
def get_scores(user):
    tag = 'appinventor_user_actionable_scores_' + user #request.form['tag']
    nb_play = 0
    sum_play = 0
    average = 0.00
    if tag:
        value = TinyWebDB.query.filter_by(tag=tag).first().value.replace("[", "").replace("]", "").split(',');
        nb_play = len(value)
        for v in value:
            sum_play = sum_play + int(v)
        nb_play = len(value)
        average = format(sum_play/nb_play, '.2f')
        return jsonify(['VALUE', 'nb', nb_play, 'sum', sum_play, 'average', average])
        ## return jsonify(['VALUE', 'average', math.ceil(sum_play/nb_play)])
    return 'Invalid user: '+user

@app.route('/getscores/actionable/users') #, methods=['POST'])
def get_averages():
    tag_users = 'appinventor_users' #'appinventor_user_actionable_scores_ranking'
    users = TinyWebDB.query.filter_by(tag=tag_users).first().value.replace("[", "").replace("]", "").replace('"', '').split(',');
    board = ''
   
    for user in users:
        tag = 'appinventor_user_actionable_scores_' + user       
        board += '<br>' + tag
        nb_play = 0
        sum_play = 0
        average = 0.00
        value = TinyWebDB.query.filter_by(tag=tag).first().value.replace("[", "").replace("]", "").split(',');
        if value:
             board += '<br>' + value
         #   nb_play = len(value)
         #   for v in value:
         #       sum_play = sum_play + int(v)
         #   nb_play = len(value)
         #   average = format(sum_play/nb_play, '.2f')
         #   board += user + ': ' + ['VALUE', 'nb', nb_play, 'sum', sum_play, 'average', average]) + '<\br>'
    return board


@app.route('/deleteentry')
def delete_entry():
#     docs = db.search(User.name == 'John')
#     for doc in docs:
#     db.session.remove(where('value') == '')
#     db.session.commit()
#     return 'Empty entries have been deleted!'
    return 'Not yet implemented!'


if __name__ == '__main__':
    app.run()

