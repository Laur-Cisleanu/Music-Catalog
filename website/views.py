from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# from .models import Songs
from os import path
from . import app, db, cursor

views = Blueprint('views', __name__)

UPLOAD_FOLDER = r'D:\Azimut curs online Python\efwfwefwefweew\website\uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
@login_required
def home():
    cursor.execute('SELECT author, title, username FROM songs')
    songs = cursor.fetchall()
    return render_template("home.html", user = current_user, songs = songs)

@views.route('/add_song', methods = ['POST', 'GET'])
@login_required
def add_song():
    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']
        user = current_user.username
        user_id = current_user.user_id

        if 'location' not in request.files:
            flash('no file part')
            return redirect(request.url)
        file = request.files['location']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(path.join(app.config['UPLOAD_FOLDER'], filename))

            # add a duplicate verification

            cursor.execute('INSERT INTO songs (title, location, author, username, user_id) VALUES (?, ?, ?, ?, ?)', 
                           (title, filename, author, user, user_id))
            db.commit()

            # new_song = Songs(data = filename, user_id = current_user.id)
            # db.session.add(new_song)
            # db.session.commit()

            return redirect(url_for('views.home', name=filename))

    return render_template("add_song.html", user = current_user)

@views.route('/delete_song/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_song(id):
    try:
        cursor.execute('DELETE FROM songs WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('views.home'))
    except Exception as e:
        print(e)