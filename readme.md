### This can help export your Rdio collection into Spotify saved tracks

**This is forked from [jacobian](https://github.com/jacobian/rdio2spotify) -- thanks @jacobian!**

### What I did:

- removed the image part of the script
- doesn't ask for info on missing albums / artists
- edited it so it doesn't ask for any user input at all, just runs automatically
- doesn't skip albums with less than 5 songs

### OK, here's how I did this:

First, you need the same kit as I have:

- Chrome
- Python 2.7 (probably works with other versions, haven't tried).
- Rdio and Spotify accounts, natch.

Then:

1. Install the [Rdio Enhancer Chrome plugin](https://chrome.google.com/webstore/detail/rdio-enhancer/hmaalfaappddkggilhahaebfhdmmmngf?hl=en)

1. Visit Rdio in Chrome, go to your favorites view, make sure you're in "Album's & Songs" Mode (it'll be a URL like `http://www.rdio.com/people/{YOURNAME}/favorites/albums/`).

1. If Rdio Enhancer is working, you should see a "Export to CSV" button. Click it. **Wait, this takes a long time** (like, 10 minutes for my 1000-ish albums).

1. Create a [Spotify API application on this page](https://developer.spotify.com/my-applications/#!/applications)

1. Modify `r2s.py`, filling in the 4 constants up at the top with the info from the app you created above.

1. Install your Python kit: `pip install -r requirements.txt`

1. Convert the collection csv into a sqlite db you need for the next step: `python rdio_export_to_sqlite.py`

1. Run the converter! `python r2s.py`. It'll try to match albums in Rdio to equivalents in Spotify. If no results are found, you get a chance to manually enter artist/album for a search. Then, you'll see the best match, and can add it, try the next match, or skip the album entirely (for music you don't want to port over).

### Caveats

Lots, I'm sure. Here are the ones I know of:

- Doesn't do playlists. See http://soundiiz.com/.

