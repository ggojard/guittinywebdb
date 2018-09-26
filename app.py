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

## COMMUN functions ##########################
def store_a_value(tag, value):
    if tag:
        # Prevent Duplicate Key error by updating the existing tag
        existing_tag = TinyWebDB.query.filter_by(tag=tag).first()
        
        if existing_tag:
            #return 'EXISTING ' + tag + ', ' + value
            existing_tag.value = value
            db.session.commit()
        else:
            #return 'NEW ' + tag + ', ' + value
            data = TinyWebDB(tag=tag, value=value)
            db.session.add(data)
            db.session.commit()
        return jsonify(['STORED', tag, value])
    return 'Invalid Tag!'

def add_item_to_tag_value(tag, item):
    if tag:        
        existing_tag = TinyWebDB.query.filter_by(tag=tag).first()
        if existing_tag:
            current_value = existing_tag.value
            if isinstance(current_value, str):
                new_value = current_value[0:len(current_value)-1]
                new_value += ',' + str(item) + ']'
                #return tag + ', ' + item + ', ' + current_value + ', ' + new_value 
                existing_tag.value = new_value
                db.session.commit()
                return jsonify(['ADDED', tag, new_value])
            else:
                return 'Invalid value format!'
    return 'Invalid Tag!'
    
    
## WEB APP ##########################

@app.route('/')
def hello_world():
    tag = 'appinventor_user_actionable_scores_ranking'
    return 'Hello, I\'m UP!'

@app.route('/storeavalue', methods=['POST']) #OK
def store_a_value_POST():
    tag = request.form['tag']
    value = request.form['value']
    return store_a_value(tag, value)
    
   
@app.route('/getvalue', methods=['POST']) #OK
def get_value():
    tag = request.form['tag']
    if tag:
        value = TinyWebDB.query.filter_by(tag=tag).first().value
        return jsonify(['VALUE', tag, value])
    return 'Invalid Tag!'

@app.route('/deleteentry')
def delete_entry():
#     docs = db.search(User.name == 'John')
#     for doc in docs:
#     db.session.remove(where('value') == '')
#     db.session.commit()
#     return 'Empty entries have been deleted!'
    return 'Not yet implemented!'




@app.route('/actionable/user/<user>') # OK
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
    return 'Invalid user: '+user

@app.route('/actionable/getuseraverage', methods=['POST']) #OK
def get_user_average():
    user =  request.form['user']
    tag = 'appinventor_user_actionable_scores_' + user
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
    return 'Invalid user: '+user


@app.route('/actionable/getranking') #, methods=['GET', 'POST']) #OK if users  list is good
def get_ranking():
    board = []
    tag = 'appinventor_user_actionable_scores_ranking'
    users = TinyWebDB.query.filter_by(tag=tag).first().value;
    if users:
        users = users.replace("[", "").replace("]", "").replace('"', '').split(',')
        for user in users:
            tag = 'appinventor_user_actionable_scores_' + user            
            nb_play = 0
            sum_play = 0
            average = 0.00
            value = TinyWebDB.query.filter_by(tag=tag).first().value;          
            if value.find(',')>-1:
                value = value.replace("[", "").replace("]", "").split(',')
                nb_play = len(value)
                for v in value:
                    sum_play = sum_play + int(v)
                nb_play = len(value)
                average = format(sum_play/nb_play, '.2f')
                board.append([user, 'nb', nb_play, 'sum', sum_play, 'average', average])
                #board.append(value)
    return jsonify(board)

@app.route('/actionable/storeascore', methods=['POST']) #OK
def store_a_score():
    user = request.form['user']
    tag = 'appinventor_user_actionable_scores_' + user
    score = int(request.form['score'])
    return add_item_to_tag_value(tag, score)
    
@app.route('/actionable/create/user', methods=['POST']) #OK
def actionable_create_user():
    user = request.form['user']
    tag = 'appinventor_user_actionable_scores_' + user
    empty_scores = '[]'
    store_a_value(tag, empty_scores)
    tag = 'appinventor_user_actionable_scores_ranking'
    return add_item_to_tag_value(tag, '"'+user+'"')

    
    
if __name__ == '__main__':
    app.run()
    
