
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from adm.adm_utils import get_last_n_lines
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), "data", "ll.db")
db = SQLAlchemy(app)

class Dict_links(db.Model):
    __tablename__ = 'dictionary_links'
    foreign_w = db.Column('foreign_w', db.String, primary_key=True)
    link = db.Column('link', db.String)
    lang_code = db.Column('lang_code', db.Text, primary_key=True)
    date = db.Column('date', db.Integer)
    def get_date(self):
        return datetime.fromtimestamp(self.date).strftime('%d.%m.%y %H:%M')


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String)
    first_name = db.Column('first_name', db.String)
    name = db.Column('name', db.String)
    lang_code = db.Column('lang_code', db.String)
    first_access = db.Column('first_access', db.Integer)
    last_access = db.Column('last_access', db.Integer)
    shown_words_count = db.Column('shown_words_count', db.Integer)
    current_forget_rate = db.Column('current_forget_rate', db.Float)
    def get_forget_rate(self):
        if self.current_forget_rate is None:
            return -1
        else:
            return format(self.current_forget_rate*100, ".1f")

    def get_first_access(self):
        return datetime.fromtimestamp(self.first_access).strftime('%y.%m.%d %H:%M')
    def get_last_access(self):
        return datetime.fromtimestamp(self.last_access).strftime('%y.%m.%d %H:%M')
    status = db.Column('status', db.String)
    
class Word(db.Model):
    __tablename__ = 'words'
    word_id = db.Column('word_id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'))
    foreign_w = db.Column('foreign_w', db.String)
    native_w = db.Column('native_w', db.String)
    example = db.Column('example', db.String)

def get_words_with_levels(user_id):
    words = Word.query.filter_by(user_id=user_id).all()

    for word in words:
        training_data = db.session.execute(text("""
            SELECT next_training_t, last_training_t
            FROM training_cards
            WHERE user_id = :user_id AND word_id = :word_id
        """), {'user_id': user_id, 'word_id': word.word_id}).fetchall()

        tot_t = 0
        for nt, lt in training_data:
            if nt == -1 or lt == -1:
                break

            tot_t += nt - lt

        word.level = get_progr(tot_t // 2)

    return words

def get_progr(t: int):
    if t < 3600 * 6:
        return 0
    elif t < 3600 * 24:
        return 1
    elif t < 3600 * 24 * 4:
        return 2
    elif t < 3600 * 24 * 16:
        return 3
    else:
        return 4
        
# @app.route('/')
# def show_users():
#     users = User.query.order_by(User.last_access.desc()).all()        
#     return render_template('users.html', users=users)

@app.route('/')
def show_users():
    sort_by = request.args.get('sort_by', 'last_access')  # по умолчанию сортируем по last_access
    order = request.args.get('order', 'asc')  

    if order == 'desc':
        users = User.query.order_by(db.desc(sort_by)).all()
    else:
        users = User.query.order_by(db.asc(sort_by)).all()

    if 'sort_by' in request.args:  # Если приходит запрос с параметрами сортировки, возвращаем только HTML таблицы
        return render_template('users_table.html', users=users)
    else:  # Иначе возвращаем полную страницу
        return render_template('users.html', users=users)

@app.route('/dict-links')
def show_dl():
    dict_links = Dict_links.query.order_by(Dict_links.foreign_w).all()
    return render_template('dict_links.html', dict_links=dict_links)


@app.route('/words/<int:user_id>')
def show_user_words(user_id):
    words = get_words_with_levels(user_id)
    return render_template('words.html', user_id=user_id, words=words)

@app.route('/log/<int:user_id>')
def show_user_log(user_id):
    log=get_last_n_lines('log/ll.log', user_id, 100)
    return render_template('log.html', user_id=user_id, lines=log)

@app.route('/words/<int:user_id>/delete', methods=['POST'])
def delete_words(user_id):
    word_ids = request.get_json().get('word_ids')
    for word_id in word_ids:
        word = Word.query.filter_by(word_id=word_id, user_id=user_id).first()
        if word:
            db.session.delete(word)
    db.session.commit()
    return jsonify({"message": f"{len(word_ids)} words have been deleted."})

if __name__ == '__main__':
    app.run(debug=True)