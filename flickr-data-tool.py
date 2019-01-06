#!/usr/bin/env python3
"""
Flickr Data Tool

Requires Flickr data in two directories: metadata (json) and data (photo/video).

Features:
 * Recreate albums as "Title - Description" and hardlink photos/videos.
"""

import argparse
from glob import glob
import json
import os
from pprint import pprint
import shutil
import sys

def photo_handler(args, photo, album_path):
    """
    Can also be a movie file.
    """
    # print(photo)

    # TOOD Flickr file naming scheme: lower case, remove "."
    photo_path = photo["name"].lower().replace(".", "") + "_" + photo["id"] + "*"
    matches = glob(os.path.join(args.data, photo_path))
    if len(matches) == 0:
        return # TODO
        # raise Exception("FIXME no matching found")
    
    print(matches)
    
    if len(matches) > 1:
        raise Exception("FIXME multiple file match found")

    photo_dest_path = os.path.join(album_path, os.path.basename(matches[0]))
    shutil.move(matches[0], photo_dest_path)

def album_handler(args, album):
    """
    """
    print("Album: %s (id %s %d photos)" % (album["title"], album["id"], int(album["photo_count"])))
    # print(album)

    # create album directories from titles
    album_path = os.path.join(args.dest, album["title"])
    if not os.path.exists(album_path):
        try:
            os.makedirs(album_path)
        except:
            raise Exception("FIXME failed to create directory")

    for photo_id in album["photos"]:
        photo_json_path = os.path.join(args.metadata, "photo_" + photo_id + ".json")

        if not os.path.exists(photo_json_path):
            # print("%s not found" % (photo_json_path))
            continue

        with open(photo_json_path) as read_file:
            data = json.load(read_file)
            photo_handler(args, data, album_path)

def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--metadata', help="metadata path")
    parser.add_argument('--data', help="photo and video data path")
    parser.add_argument('--dest', help="destination path")

    args = parser.parse_args(arguments)

    if os.path.realpath(args.data) == os.path.realpath(args.dest):
        print("Source and Destination must be different")
        return 1

    if not os.path.exists(os.path.join(args.metadata, "albums.json")):
        raise Exception("metadata/albums.json not found")

    with open(os.path.join(args.metadata, "albums.json")) as read_file:
        data = json.load(read_file)

    if not os.path.exists(args.dest):
        os.makedirs(args.dest)

    print("Albums:", len(data["albums"]))

    # check for missing titles
    for album in data["albums"]:
        if not album["title"]:
            print(album)
            raise Exception("FIXME missing title")
        
    # check for duplicate titles
    titles = []
    titles_dup = []
    for album in data["albums"]:
        if album["title"] not in titles:
            titles.append(album["title"])
        else:
            titles_dup.append(album["title"])
    if len(titles_dup) > 0:
        print(titles_dup)
        raise Exception("FIXME duplicate album title")

    for album in data["albums"]:
        album_handler(args, album)

    # pprint(data)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
