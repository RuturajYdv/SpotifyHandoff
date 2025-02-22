import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 🔹 Replace with your Spotify API credentials
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-library-read user-library-modify user-follow-read user-follow-modify playlist-read-private playlist-modify-public playlist-modify-private"

# 🔥 Step 1: Ensure cache is deleted before login
if os.path.exists(".cache-old"):
    os.remove(".cache-old")
if os.path.exists(".cache-new"):
    os.remove(".cache-new")

# 🔹 Authenticate OLD Spotify account
SPOTIPY_OLD_CLIENT_ID = "your_old_client_id_here"
SPOTIPY_OLD_CLIENT_SECRET = "your_old_client_secret_here"

sp_old = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_OLD_CLIENT_ID,
    client_secret=SPOTIPY_OLD_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache-old",
    show_dialog=True  # Forces re-login prompt
))

# 🔥 Step 2: DELETE old account cache before logging into the new account
if os.path.exists(".cache-old"):
    os.remove(".cache-old")

# 🔹 Authenticate NEW Spotify account
SPOTIPY_NEW_CLIENT_ID = "your_new_client_id_here"
SPOTIPY_NEW_CLIENT_SECRET = "your_new_client_secret_here"

sp_new = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_NEW_CLIENT_ID,
    client_secret=SPOTIPY_NEW_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache-new",
    show_dialog=True  # Forces re-login prompt
))

# 🔹 Function to get all liked songs
def get_liked_songs(sp):
    songs = []
    results = sp.current_user_saved_tracks(limit=50)

    while results and "items" in results:
        for item in results["items"]:
            songs.append(item["track"]["id"])

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return songs

# 🔹 Function to transfer liked songs
def transfer_liked_songs(sp_old, sp_new):
    songs = get_liked_songs(sp_old)

    for i in range(0, len(songs), 50):  # Add in batches of 50 (Spotify limit)
        sp_new.current_user_saved_tracks_add(songs[i:i+50])

    print(f"✅ {len(songs)} liked songs transferred successfully!")

# 🔹 Function to get followed artists
def get_followed_artists(sp):
    artists = []
    results = sp.current_user_followed_artists(limit=50)

    while results and "artists" in results:
        for item in results["artists"]["items"]:
            artists.append(item["id"])

        if results["artists"]["next"]:
            results = sp.next(results["artists"])
        else:
            break

    return artists

# 🔹 Function to transfer followed artists
def transfer_followed_artists(sp_old, sp_new):
    artists = get_followed_artists(sp_old)

    for i in range(0, len(artists), 50):
        sp_new.user_follow_artists(artists[i:i+50])

    print(f"✅ {len(artists)} followed artists transferred successfully!")

# 🔹 Function to get all playlists
def get_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()

    while results and "items" in results:
        for item in results["items"]:
            playlists.append({
                "id": item["id"],
                "name": item["name"]
            })

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return playlists

# 🔹 Function to get tracks from a playlist
def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)

    while results and "items" in results:
        for item in results["items"]:
            if item["track"]:
                tracks.append(item["track"]["id"])

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return tracks

# 🔹 Function to transfer playlists
def transfer_playlists(sp_old, sp_new):
    playlists = get_playlists(sp_old)
    user_id = sp_new.me()["id"]

    for playlist in playlists:
        print(f"🔄 Creating playlist: {playlist['name']}...")

        # Create new playlist
        new_playlist = sp_new.user_playlist_create(user_id, playlist["name"], public=True)
        new_playlist_id = new_playlist["id"]

        # Get tracks from old playlist
        tracks = get_playlist_tracks(sp_old, playlist["id"])

        # Add tracks in batches of 50
        for i in range(0, len(tracks), 50):
            sp_new.playlist_add_items(new_playlist_id, tracks[i:i+50])

        print(f"✅ Playlist '{playlist['name']}' transferred successfully!")

# 🚀 Start Transfer Process
print("🔑 Logging into old account...")
print("✅ Successfully authenticated OLD account!")

print("\n🔑 Logging into new account...")
print("✅ Successfully authenticated NEW account!")

print("\n🎵 Transferring liked songs...")
transfer_liked_songs(sp_old, sp_new)

print("\n🎤 Transferring followed artists...")
transfer_followed_artists(sp_old, sp_new)

print("\n📂 Transferring playlists...")
transfer_playlists(sp_old, sp_new)

print("\n🎉 Transfer complete! Check your new Spotify account.")
