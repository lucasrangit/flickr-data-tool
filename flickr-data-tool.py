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

photos_processed = list()

def photo_get_path(args, photo_json):
    # TOOD Flickr file naming scheme: lower case, remove "."
    photo_path = photo_json["name"].lower().replace(".", "") + "_" + photo_json["id"] + "*"

    matches = glob(os.path.join(args.src, photo_path))

    # skip not found (allows restart if interrupted)
    if len(matches) == 0:
        return # skip and don't assume processed

    if len(matches) > 1:
        print(matches)
        raise Exception("FIXME multiple file match found")

    return matches[0]

def photo_handler(args, photo, album_path):
    """
    Can also be a movie file.

    """
    print("Photo: %s (id %s albums %d)" % (photo["name"], photo["id"], len(photo["albums"])))
    # print(photo)

    # validate
    # TODO photo["albums"] is not reliable and may not match the data in albums.json
    
    # get path
    photo_path = photo_get_path(args, photo)
    if not photo_path:
        return

    # track
    if photo["id"] in photos_processed:
        print(photo)
        raise Exception("FIXME multiple destination albums")
    photos_processed.append(photo["id"])

    # organize
    photo_dest_path = os.path.join(album_path, os.path.basename(photo_path))
    shutil.move(photo_path, photo_dest_path)

def album_handler(args, album):
    """
    """
    print("Album: %s (id %s %d photos)" % (album["title"], album["id"], int(album["photo_count"])))
    # print(album)

    # create album directories from titles
    album_path = os.path.join(args.dst, album["title"])
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
    parser.add_argument('--src', help="path to source photo and video files")
    parser.add_argument('--dst', help="path to source files organized in albums")

    args = parser.parse_args(arguments)

    if os.path.realpath(args.src) == os.path.realpath(args.dst):
        print("Source and Destination must be different")
        return 1

    if not os.path.exists(os.path.join(args.metadata, "albums.json")):
        raise Exception("metadata/albums.json not found")

    with open(os.path.join(args.metadata, "albums.json")) as read_file:
        data = json.load(read_file)

    if not os.path.exists(args.dst):
        os.makedirs(args.dst)

    print("Albums:", len(data["albums"]))

    # all albums must have titles
    for album in data["albums"]:
        if not album["title"]:
            print(album)
            raise Exception("FIXME missing album title")
        
    # all albums titles must be unique
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
