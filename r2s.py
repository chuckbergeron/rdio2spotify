# -*- coding: utf-8 -*-
import base64
import click
import pathlib
import spotipy
import spotipy.util
import sqlite3
import time
import urllib
from more_itertools import chunked
from pprint import pprint

# FILL THESE IN YOURSELF:
USERNAME = 'FILLIN'
CLIENT_ID = 'FILLIN'
CLIENT_SECRET = 'FILLIN'
REDIRECT_URI = 'FILLIN'

class SkipAlbum(Exception):
    pass


def main():
    spotify = connect_to_spotify()

    here = pathlib.Path(__file__).parent
    collection_db_file = here / 'collection.sqlite3'
    if not collection_db_file.exists():
        click.secho("collection.sqlite3 doesn't exist, run rdio_export_to_sqlite3.py first", fg='red')
        return

    db = sqlite3.connect(str(collection_db_file))
    cursor = db.cursor()
    cursor.execute('''SELECT artist, album
                      FROM collection
                      WHERE skip = 0
                      AND complete = 0
                      ORDER BY track_count DESC''')

    all_albums = cursor.fetchall()
    for i, (artist, album) in enumerate(all_albums):
        print_header(artist, album, i, len(all_albums))
        results = spotify.search(q=u'artist:"{0}" album:"{1}"'.format(artist, album), type='album')

        try:
            album_object = select_album(artist, album, results['albums']['items'], i, len(all_albums))
        except SkipAlbum:
            continue

        if album_object:
            add_to_spotify(db, spotify, album_object, artist, album)
        else:
            continue

    db.close()


def connect_to_spotify():
    token = spotipy.util.prompt_for_user_token(USERNAME,
        scope='user-library-modify',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI)
    return spotipy.Spotify(auth=token)


def print_header(artist, album, current, total):
    click.clear()
    title = u'{0} - {1}'.format(artist, album)
    progress = u'{0}/{1}'.format(current+1, total)
    term_width, term_height = click.get_terminal_size()
    pad_width = (term_width - len(title) - len(progress)) - 10
    header_template = u'=== {title} {pad} {progress} ==='
    click.secho(
        header_template.format(
            title=title,
            pad='=' * pad_width,
            progress=progress,
        ),
        bg='blue', fg='white'
    )



def select_album(original_artist, original_album, albums, current_position, total_number):
    for album in albums:
        print_header(original_artist, original_album, current_position, total_number)
        click.secho(u'\nFound: "{0}"\n'.format(album['name']), fg='green')

        return album


def add_to_spotify(db, spotify, album, original_artist, original_album):
    album = spotify.album(album['uri'])
    tracks = album['tracks']
    track_ids = [t['uri'] for t in tracks['items']]
    while tracks['next']:
        tracks = spotify.next(tracks)
        track_ids.extend(t['uri'] for t in tracks['items'])

    click.echo('Adding {0} tracks to Spotify...'.format(len(track_ids)))
    for chunk in chunked(track_ids, 50):
        response = spotify.current_user_saved_tracks_add(chunk)
        if response is not None:
            click.secho('Fuck, something broke:')
            pprint(response)
            click.confirm('Continue?', abort=True)
            return

    cursor = db.cursor()
    cursor.execute('''UPDATE collection SET complete = 1
                      WHERE artist = ? AND album = ?''',
                   [original_artist, original_album])
    db.commit()
    click.secho('Done ', fg='green', nl=False)
    time.sleep(0.25)



def under_first(s):
    return click.style(s[0], underline=True) + s[1:]


if __name__ == '__main__':
    try:
        main()
    except click.exceptions.Abort:
        pass
