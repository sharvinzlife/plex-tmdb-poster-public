# 🎬 Plex TMDB Poster Updater 🖼️

Automatically update your Plex movie posters with the latest TMDB artwork! 🌟

## 🚀 Features

- 🔄 Auto-update posters for newly added movies
- 📚 Bulk update entire libraries
- 🔒 Option to include or exclude locked posters
- 🧪 Dry-run mode for safe testing

## 🛠️ Requirements

- 🐍 Python 3.x
- 📦 plexapi
- 🔑 python-dotenv

## 🏗️ Setup

1. 📥 Download and extract to your Tautulli scripts folder
2. 🔧 Install required Python libraries:
   ```
   pip install plexapi python-dotenv
   ```
3. 📄 Copy `.env.example` to `.env` and fill in your Plex URL and token
4. ⚙️ Configure Tautulli notification agent
5. 🔑 Set up your Plex URL and Token (if not using .env file)

## 🎮 Usage

```bash
# Update entire library
python select_tmdb_poster.py --library "Movies"

# Update specific movie
python select_tmdb_poster.py --rating_key 1234

# Include locked posters
python select_tmdb_poster.py --library "Movies" --include_locked

# Dry run
python select_tmdb_poster.py --library "Movies" --dry-run
```

## 🔗 Tautulli Integration

- 🔔 Trigger: Recently Added
- 🎯 Condition: Media Type is movie
- 💻 Argument: --rating_key {rating_key}

Keep your Plex library looking fresh with automatic TMDB poster updates! 🌈✨