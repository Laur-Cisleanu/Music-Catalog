from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# from .models import Songs
import random
from os import path
from . import app, db, cursor

views = Blueprint('views', __name__)

UPLOAD_FOLDER = r'D:\Python\Projects\Music-Catalog\website\static\uploads'
ALLOWED_EXTENSIONS = {'mp3', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
@login_required
def home():
    cursor.execute('SELECT author, title, username, location, id FROM songs')
    songs = cursor.fetchall()

    cursor.execute('SELECT * FROM playlists WHERE user_id = ?', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("home.html", user = current_user, songs = songs, playlists = playlists)

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

@views.route('/view_playlists')
@login_required
def view_playlists():
    cursor.execute('SELECT name, user_id, username FROM playlists')
    playlists = cursor.fetchall()
    return render_template("view_playlists.html", user = current_user, playlists = playlists)

@views.route('/create_playlist')
@login_required
def create_playlist(song_id):
    cursor.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
    song = cursor.fetchall()

    playlist_id = random.randint(100000, 999999)
    name = request.form['name']
    user_id = current_user.user_id
    username = current_user.username
    song_id = song.id
    title = song.title
    entry = 1
    private = 0
    cursor.execute("""INSERT INTO playlists (playlist_id, name, user_id, username, song_id, title, entry, private)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (playlist_id, name, user_id, username, song_id, title, entry, private))
    db.commit()
    return redirect(url_for('views.home'))