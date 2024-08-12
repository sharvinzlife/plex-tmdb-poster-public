#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description:  Selects the default TMDB poster if no poster is selected
              or the current poster is from Gracenote.
Author:       /u/sharvinzlife
Requires:     plexapi, python-dotenv
Usage:
    * Change the posters for an entire library:
        python select_tmdb_poster.py --library "Movies"
    * Change the poster for a specific item:
        python select_tmdb_poster.py --rating_key 1234
    * By default locked posters are skipped. To update locked posters:
        python select_tmdb_poster.py --library "Movies" --include_locked
    * To preview changes without applying them:
        python select_tmdb_poster.py --library "Movies" --dry-run
Tautulli script trigger:
    * Notify on recently added
Tautulli script conditions:
    * Filter which media to select the poster. Examples:
        [ Media Type | is | movie ]
Tautulli script arguments:
    * Recently Added:
        --rating_key {rating_key}
'''
import argparse
import os
import logging
import sys
from dotenv import load_dotenv
import requests
from plexapi.server import PlexServer
from plexapi.exceptions import PlexApiException

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='tmdb_poster_script.log', filemode='a')
logger = logging.getLogger(__name__)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# Load environment variables
load_dotenv()

# Get Plex URL and token from environment variables
PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')

logger.debug(f"Script started. PLEX_URL: {'Set' if PLEX_URL else 'Not set'}, PLEX_TOKEN: {'Set' if PLEX_TOKEN else 'Not set'}")

if not PLEX_URL or not PLEX_TOKEN:
    logger.error("PLEX_URL or PLEX_TOKEN not set in environment variables.")
    sys.exit(1)

def is_poster_locked(item):
    return any(field.name == 'thumb' and field.locked for field in item.fields)

def select_tmdb_poster_library(library, include_locked=True, dry_run=False):
    try:
        for item in library.all():
            select_tmdb_poster_item(item, include_locked=include_locked, dry_run=dry_run)
    except PlexApiException as e:
        logger.error(f"Error processing library: {e}")

def select_tmdb_poster_item(item, include_locked=True, dry_run=False):
    try:
        if not include_locked and is_poster_locked(item):
            logger.info(f"Locked poster for {item.title}. Skipping.")
            return
        posters = item.posters()
        selected_poster = next((p for p in posters if p.selected), None)
        if selected_poster is None:
            logger.warning(f"No poster selected for {item.title}.")
        else:
            skipping = ' Skipping.' if selected_poster.provider != 'gracenote' else ''
            logger.info(f"Poster provider is '{selected_poster.provider}' for {item.title}.{skipping}")
        if posters and (selected_poster is None or selected_poster.provider == 'gracenote'):
            tmdb_poster = next((p for p in posters if p.provider == 'tmdb'), posters[0])
            if not dry_run:
                tmdb_poster.select()
                logger.info(f"Selected {tmdb_poster.provider} poster for {item.title}.")
            else:
                logger.info(f"[DRY RUN] Would select {tmdb_poster.provider} poster for {item.title}.")
    except PlexApiException as e:
        logger.error(f"Error processing item {item.title}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rating_key', type=int)
    parser.add_argument('--library')
    parser.add_argument('--include_locked', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help="Preview changes without applying them")
    opts = parser.parse_args()

    logger.debug(f"Arguments: rating_key={opts.rating_key}, library={opts.library}, include_locked={opts.include_locked}, dry_run={opts.dry_run}")

    try:
        # Create a custom session that ignores SSL verification
        session = requests.Session()
        session.verify = False
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()

        # Use the custom session when creating the PlexServer instance
        plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=session)
        logger.info("Successfully connected to Plex server")
        if opts.rating_key:
            item = plex.fetchItem(opts.rating_key)
            select_tmdb_poster_item(item, opts.include_locked, opts.dry_run)
        elif opts.library:
            library = plex.library.section(opts.library)
            select_tmdb_poster_library(library, opts.include_locked, opts.dry_run)
        else:
            logger.warning("No --rating_key or --library specified. Script will exit without changes.")
    except PlexApiException as e:
        logger.error(f"Error connecting to Plex server: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()
    logger.debug("Script finished executing")