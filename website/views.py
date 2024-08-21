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
    cursor.execute('SELECT author, title, username, location, id, genre FROM songs')
    songs = cursor.fetchall() 
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("home.html", user = current_user, songs = songs, playlists = playlists)

@views.route('/sort/<sort_by>/<order>')
@login_required
def sort(sort_by, order):
    cursor.execute(f'SELECT author, title, username, location, id, genre FROM songs ORDER BY {sort_by} {order}')
    songs = cursor.fetchall() 
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("home.html", user = current_user, songs = songs, playlists = playlists, 
                            sort_by = sort_by, order = order)

@views.route('/search', methods = ['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        search_by = f'%{request.form['search_by']}%'
        cursor.execute("""SELECT author, title, username, location, id, genre FROM songs 
                       WHERE  title LIKE ? OR author LIKE ? OR username LIKE ? OR genre LIKE ?""", 
                       (search_by, search_by, search_by, search_by, ))
        songs = cursor.fetchall()
        cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
        playlists = cursor.fetchall()
        
        return render_template("search.html", user = current_user, songs = songs, playlists = playlists, 
                                search_by = search_by)
    
@views.route('/search/<sort_by>/<order>')
@login_required
def search_sort(sort_by, order):
    search_by = request.args.get('search_by')
    cursor.execute(f"""SELECT author, title, username, location, id, genre FROM songs 
                   WHERE  title LIKE ? OR author LIKE ? OR username LIKE ? OR genre LIKE ?
                   ORDER BY {sort_by} {order}""", (search_by, search_by, search_by, search_by, ))
    songs = cursor.fetchall()
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()
    return render_template("search.html", user = current_user, songs = songs, playlists = playlists, 
                            search_by = search_by, sort_by = sort_by, order = order)

@views.route('/add_song', methods = ['POST', 'GET'])
@login_required
def add_song():
    if request.method == 'POST':

        author = request.form['author']
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
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

            cursor.execute("""INSERT INTO songs (title, location, author, genre, description, username, user_id) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)""", (title, filename, author, genre, description, user, user_id))
            db.commit()

            # new_song = Songs(data = filename, user_id = current_user.id)
            # db.session.add(new_song)
            # db.session.commit()

            return redirect(url_for('views.home', name=filename))

    return render_template("add_song.html", user = current_user)

@views.route('/edit_song/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_song(id):
    cursor.execute('SELECT * FROM songs WHERE id = ?', (id, ))
    song = cursor.fetchone()
    user_id = song[6]
    
    if user_id == current_user.user_id:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            description = "" + request.form['description']

            cursor.execute('UPDATE songs SET title = ?, author = ?, genre = ?, description = ? WHERE id = ?', 
                           (title, author, genre, description, id))
            db.commit()
            return redirect(url_for('views.home'))
        
        return render_template("edit_song.html", user = current_user, song = song)
    else:
        flash('You don\'t have access', category = 'error')
    return redirect(url_for('views.home'))
        
@views.route('/delete_song/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_song(id):
    cursor.execute('SELECT * FROM songs WHERE id = ?', (id, ))
    song = cursor.fetchone()
    user_id = song[6]

    if user_id == current_user.user_id:
        try:
            cursor.execute('DELETE FROM songs WHERE id = ?', (id,))
            cursor.execute('DELETE FROM playlists WHERE song_id = ?', (id,))
            db.commit()
            return redirect(url_for('views.home'))
        except Exception as e:
            print(e)
    else:
        flash('You don\'t have access', category = 'error')
        return redirect(url_for('views.home'))
    

@views.route('/view_playlists')
@login_required
def view_playlists():
    cursor.execute('SELECT * FROM playlists WHERE entry = 1')
    playlists = cursor.fetchall()
    return render_template("view_playlists.html", user = current_user, playlists = playlists)

@views.route('/create_playlist/<int:song_id>', methods = ['POST', 'GET'])
@login_required
def create_playlist(song_id):
    if request.method == 'POST':
        cursor.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
        song = cursor.fetchone()
    
        playlist_id = random.randint(100000, 999999)
        name = request.form['name']
        user_id = current_user.user_id
        username = current_user.username
        song_id = song[0]
        title = song[1]
        author = song[3]
        entry = 1
        private = 0
        cursor.execute("""INSERT INTO playlists (playlist_id, name, user_id, username, song_id, title, 
                       author, entry, private) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (playlist_id, name, user_id, username, song_id, title, author, entry, private))
        db.commit()
        return redirect(url_for('views.home'))

@views.route('/add_to_playlist/<int:playlist_id>/<int:song_id>')
@login_required
def add_to_playlist(playlist_id, song_id):
    user_id = current_user.user_id
    cursor.execute('SELECT name, private FROM playlists WHERE playlist_id = ? AND user_id = ?',
                   (playlist_id, user_id))
    playlist = cursor.fetchone()
    name = playlist[0]
    user_id = current_user.user_id
    username = current_user.username
    cursor.execute('SELECT title, author FROM songs WHERE id = ?', (song_id,))
    song_info = cursor.fetchone()
    title = song_info[0]
    author = song_info[1]
    cursor.execute('SELECT COUNT(entry) FROM playlists WHERE playlist_id = ? AND user_id = ?', (playlist_id, user_id))
    entry = cursor.fetchone()[0]
    entry += 1
    private = playlist[1]
    cursor.execute("""INSERT INTO playlists (playlist_id, name, user_id, username, song_id, title, author, entry, private)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (playlist_id, name, user_id, username, song_id, title, author, entry, private))
    db.commit()
    return redirect(url_for('views.home'))

@views.route('/view_playlist/<int:playlist_id>')
@login_required
def view_playlist(playlist_id):
    cursor.execute('SELECT author, title, username, song_id, entry, name FROM playlists WHERE playlist_id = ?',
                   (playlist_id,))
    songs = cursor.fetchall()
    playlist_name = songs[0][5]
    cursor.execute('SELECT location FROM songs WHERE id = ?', (songs[0][3],))
    location = cursor.fetchone()

    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("view_playlist.html", user = current_user, songs = songs, 
                           location = location[0], playlist_name = playlist_name, playlists = playlists)