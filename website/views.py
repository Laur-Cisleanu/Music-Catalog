from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import random
from os import path
from . import app, db, cursor
from .utils import allowed_file

views = Blueprint('views', __name__)

UPLOAD_FOLDER = r'D:\Python\Projects\Music-Catalog\website\static\uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@views.route('/')
@login_required
def home():
    cursor.execute('SELECT author, title, username, location, id, genre, user_id FROM songs ORDER BY id desc')
    songs = cursor.fetchall() 
    
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()
    
    cursor.execute('SELECT * FROM playlists WHERE entry = 1 ORDER BY id desc')
    playlist_view = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM playlists WHERE entry = 1')
    list_index = cursor.fetchone()[0]
    if list_index > 8:
        list_index = 8

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT DISTINCT genre FROM songs')
    genres = cursor.fetchall()
    genres_len = len(genres)
    return render_template("home.html", user = current_user, songs = songs, playlists = playlists, users_info = users_info,
                           playlist_view = playlist_view, list_index = list_index, genres = genres, genres_len = genres_len)

@views.route('/sort/<sort_by>/<order>')
@login_required
def sort(sort_by, order):
    if not sort_by:
        sort_by = 'title'
    if not order:
        order = 'asc'

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute(f'SELECT author, title, username, location, id, genre, user_id FROM songs ORDER BY {sort_by} {order}')
    songs = cursor.fetchall()
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("songs.html", user = current_user, songs = songs, playlists = playlists, 
                            sort_by = sort_by, order = order, users_info = users_info)

@views.route('/search', methods = ['POST', 'GET'])
@login_required
def search():
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    if request.args.get('search_in'):
        search_by = request.args.get('search_by')
        search_in = request.args.get('search_in')
        order = request.args.get('order')
        cursor.execute(f"""SELECT author, title, username, location, id, genre FROM songs
                        WHERE {search_in} LIKE ? ORDER BY {search_in} {order}""", (search_by, ))
        songs = cursor.fetchall()
        return render_template("search.html", user = current_user, songs = songs, playlists = playlists, 
                                search_by = search_by,sort_by = search_in, order = order, users_info = users_info)

    if request.method == 'POST':
        search_by = f'%{request.form['search_by']}%'
        cursor.execute("""SELECT author, title, username, location, id, genre FROM songs 
                       WHERE  title LIKE ? OR author LIKE ? OR username LIKE ? OR genre LIKE ?""", 
                       (search_by, search_by, search_by, search_by, ))
        songs = cursor.fetchall()    
        
        return render_template("search.html", user = current_user, songs = songs, playlists = playlists, 
                                search_by = search_by, sort_by = 'title', order = 'asc', users_info = users_info)
    
@views.route('/search/<sort_by>/<order>')
@login_required
def search_sort(sort_by, order):
    search_by = request.args.get('search_by')
    
    if not sort_by:
        sort_by = 'title'
    if not order:
        order = 'asc'

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute(f"""SELECT author, title, username, location, id, genre FROM songs 
                   WHERE  title LIKE ? OR author LIKE ? OR username LIKE ? OR genre LIKE ?
                   ORDER BY {sort_by} {order}""", (search_by, search_by, search_by, search_by, ))
    songs = cursor.fetchall()
    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()
    return render_template("search.html", user = current_user, songs = songs, playlists = playlists, 
                            search_by = search_by, sort_by = sort_by, order = order, users_info = users_info)

@views.route('/add_song', methods = ['POST', 'GET'])
@login_required
def add_song():
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    if request.method == 'POST':

        author = request.form['author']
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        user = current_user.username
        user_id = current_user.user_id

        if 'location' not in request.files:
            flash('no file part', category = 'error')
            return redirect(request.url)
        file = request.files['location']

        if file.filename == '':
            flash('No selected file', category = 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor.execute("""INSERT INTO songs (title, location, author, genre, description, username, user_id) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)""", (title, filename, author, genre, description, user, user_id))
            db.commit()

            flash('Song added with success!', category = 'success')
            return redirect(url_for('views.home', name=filename))

    return render_template("add_song.html", user = current_user, users_info = users_info)

@views.route('/view_song/<int:id>')
@login_required
def view_song(id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM songs WHERE id = ?', (id, ))
    song = cursor.fetchone()

    return render_template('view_song.html', user = current_user, song = song, users_info = users_info)

@views.route('/edit_song/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_song(id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM songs WHERE id = ?', (id, ))
    song = cursor.fetchone()
    user_id = song[6]
    
    if user_id == current_user.user_id or current_user.admin == 1:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            description = "" + request.form['description']

            cursor.execute('UPDATE songs SET title = ?, author = ?, genre = ?, description = ? WHERE id = ?', 
                           (title, author, genre, description, id))
            db.commit()
            flash('Song has been updated successfully!', category = 'success')
            return redirect(url_for('views.home'))
        
        return render_template("edit_song.html", user = current_user, song = song, users_info = users_info)
    else:
        flash('You don\'t have access', category = 'error')
    return redirect(url_for('views.home'))
        
@views.route('/delete_song/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_song(id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM songs WHERE id = ?', (id, ))
    song = cursor.fetchone()
    user_id = song[6]

    if current_user.user_id == user_id or current_user.admin == 1:
        try:
            cursor.execute('DELETE FROM songs WHERE id = ?', (id,))
            cursor.execute('DELETE FROM playlists WHERE song_id = ?', (id,))
            db.commit()

            flash('Song deleted successfully', category = 'success')
            return redirect(url_for('views.home'))
        except Exception as e:
            print(e)
    else:
        flash('You don\'t have access', category = 'error')
        return redirect(url_for('views.home'))
    

@views.route('/view_playlists')
@login_required
def view_playlists():
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM playlists WHERE entry = 1')
    playlists = cursor.fetchall()
    return render_template("view_playlists.html", user = current_user, playlists = playlists, users_info = users_info)

@views.route('/create_playlist/<int:song_id>', methods = ['POST', 'GET'])
@login_required
def create_playlist(song_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

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
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

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
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT author, title, username, song_id, entry, name FROM playlists WHERE playlist_id = ?',
                   (playlist_id,))
    songs = cursor.fetchall()
    playlist_name = songs[0][5]
    cursor.execute('SELECT location FROM songs WHERE id = ?', (songs[0][3],))
    location = cursor.fetchone()

    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template("view_playlist.html", user = current_user, songs = songs, users_info = users_info,
                           location = location[0], playlist_id = playlist_id, playlist_name = playlist_name, playlists = playlists)

@views.route('edit_playlist/<int:playlist_id>', methods = ['POST', 'GET'])
@login_required
def edit_playlist(playlist_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM songs JOIN playlists ON songs.id = playlists.song_id WHERE playlists.playlist_id = ?', 
                   (playlist_id, ))
    playlist = cursor.fetchall()
    user_id = playlist[0][11]

    if user_id == current_user.user_id or current_user.admin == 1:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            private = request.form['private']

            cursor.execute('UPDATE playlists SET name = ?, description = ?, private = ? WHERE playlist_id = ?', 
                            (name, description, private, playlist_id))
            db.commit()
            return redirect(url_for('views.view_playlist', playlist_id = playlist_id))
    else:
        flash('You don\'t have access', category = 'error')
        return redirect(url_for('views.view_playlist', playlist_id = playlist_id))
    return render_template('edit_playlist.html', user = current_user, playlist = playlist, users_info = users_info)

@views.route('delete_playlist/<int:playlist_id>')
@login_required
def delete_playlist(playlist_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone()

    cursor.execute('SELECT * FROM playlists WHERE playlist_id = ?', (playlist_id, ))
    playlist = cursor.fetchall()
    user_id = playlist[0][3]
    song_entry = request.args.get('song_entry')
    print (type(playlist[-1][8]))
    if current_user.user_id == user_id or current_user.admin == 1:
        if song_entry:
            cursor.execute('DELETE FROM playlists WHERE entry = ? AND playlist_id = ?', (song_entry, playlist_id))
            db.commit()
            cursor.execute('SELECT COUNT(entry) FROM playlists WHERE playlist_id = ?', (playlist[0][1], ))
            entry_count = cursor.fetchone()[0]
            cursor.execute('SELECT * FROM playlists WHERE playlist_id = ?', (playlist_id, ))
            song = cursor.fetchall()
            
            for i in range(entry_count):
                if song[i][8] > i+1:
                    cursor.execute('UPDATE playlists SET entry = ? WHERE entry = ?', (i+1, song[i][8]))
                    db.commit()

            flash("Song removed from the playlist successfully", category = 'success')
            return redirect(url_for('views.edit_playlist', playlist_id = playlist_id))
    
        try:
            cursor.execute('DELETE FROM playlists WHERE playlist_id = ?', (playlist_id,))
            db.commit()
            return redirect(url_for('views.view_playlists'))
        except Exception as e:
            print(e)
    else:
        flash('You don\'t have access', category = 'error')
        return redirect(url_for('views.view_playlist', playlist_id = playlist_id))
    
@views.route('profile/<user_id>')
@login_required
def profile(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id, ))
    user_info = cursor.fetchone()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone() 

    cursor.execute('SELECT * FROM songs WHERE user_id = ?', (user_id, ))
    user_songs_info = cursor.fetchall()

    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (user_id, ))
    user_playlists_info = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM playlists WHERE user_id = ? AND entry = 1', (user_id, ))
    playlist_count = range(cursor.fetchone()[0])

    cursor.execute('SELECT * FROM playlists WHERE user_id = ? AND entry = 1', (current_user.user_id,))
    playlists = cursor.fetchall()

    return render_template('profile.html', user = current_user, user_id = user_id, user_info = user_info, users_info = users_info,
                           user_songs_info = user_songs_info, user_playlists_info = user_playlists_info, 
                           playlist_count = playlist_count, playlists = playlists)

@views.route('edit_profile/<user_id>', methods = ['GET', 'POST'])
@login_required
def edit_profile(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id, ))
    user_info = cursor.fetchone()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (current_user.user_id, ))
    users_info = cursor.fetchone() 

    if current_user.user_id == user_info[0] or current_user.admin == 1:
        if request.method == 'POST':
            if 'profile_picture' not in request.files:
                flash('No file part', category = 'error')
                return redirect(request.url)

            username = request.form['username']
            description = request.form['description']
            file = request.files['profile_picture']

            if file.filename == '':
                flash('No selected file', category = 'error')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(path.join(app.config['UPLOAD_FOLDER'], filename))  

                cursor.execute('UPDATE users SET username = ?, user_description = ?, profile_picture = ? WHERE user_id = ?', 
                               (username, description, filename, user_id))
                db.commit()

                flash('Profile updated successfully!', category = 'success')
                return redirect(url_for('views.profile', user_id = user_id))
            else:
                flash('invalid photo/data', category = 'error')
                return redirect(request.url)
    
    else:
        flash('You don\'t have access', category = 'error')
        return redirect(url_for('views.profile', user_id = user_id))
        
    return render_template('edit_profile.html', user = current_user, user_id = user_id, user_info = user_info, users_info = users_info)
        
    