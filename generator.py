#! /usr/bin/env python3

""" Generates the Pandoras Box SDK """

import argparse
import jinja2
import json
import sys
from datetime import datetime
from io import open
from os import listdir, path, makedirs
from inflection import underscore, camelize
from markdown2 import Markdown
from hashlib import sha1

__author__ = 'Dennis Kuypers'

BASE_PATH = path.dirname(path.abspath(__file__))


def create_path_for_file(filename):
    pathname = path.dirname(filename)
    if not path.exists(pathname):
        makedirs(pathname)


def hash_file(filename):
    hasher = sha1()
    with open(filename, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def main(regenerate=False):
    # store timestamp
    now = str(datetime.now().date())

    # load db & config
    db = json.load(open(path.join(BASE_PATH, "db.json")))
    config = json.load(open(path.join(BASE_PATH, "config.json")))

    # db: replace chunk IDs with reference to actual data
    for c in db['commands']:
        for direction in ['send', 'recv']:
            for i in range(len(c[direction])):
                c[direction][i] = db['chunks'][str(c[direction][i])]

    # check if the PB revision has changed
    rev_changed = config['revision'] != db['revision']

    for job in config['jobs']:
        template_loader = jinja2.FileSystemLoader(
            searchpath=[
                        path.join(BASE_PATH, "source", "_common"),
                        path.join(BASE_PATH, "source", job['src'])
                        ]
            )
        jinja2_env = jinja2.Environment(loader=template_loader)
        jinja2_env.filters['underscore'] = underscore
        jinja2_env.filters['camelize'] = camelize
        jinja2_env.filters['camelize_small'] = lambda s: camelize(s, False)
        jinja2_env.filters['no_suffix'] = lambda s: '_'.join(s.split('_')[:-1]) or s
        jinja2_env.filters['is_buffer'] = lambda s: s[-7:] == '_buffer'

        output_directory = path.abspath(path.join(BASE_PATH, "..", job['name']))

        # push version if there are any changes
        any_changed = any([hash_file(jinja2_env.get_template(jf['src']).filename) != jf['hash'] for jf in job['files']])
        if rev_changed or any_changed and not regenerate:
            job['version_minor'] = job['version_minor'] + 1

        for job_file in job['files']:
            template = jinja2_env.get_template(job_file['src'])
            template_hash = hash_file(template.filename)

            if not rev_changed and not any_changed:
                print("Skipping", template.filename[len(BASE_PATH):])
                continue

            data = {**db,
                    'lang': job['name'],
                    'version': '.'.join((
                            str(job['version_major']),
                            str(job['version_minor']),
                            str(db['revision'])
                            )),
                    'time': now
                    }

            if 'vars' in job_file:
                data.update(job_file['vars'])

            dst_file = job_file['src']
            if 'dst' in job_file:
                dst_file = job_file['dst']

            # prepare path for file
            output_file = path.join(output_directory, dst_file)
            create_path_for_file(output_file)

            with open(output_file, 'w') as outfile:
                outfile.write(template.render(data))

            # update hash
            job_file['hash'] = template_hash

    if rev_changed:
        config['revision'] = db['revision']

    json.dump(
        config,
        open(path.join(BASE_PATH, "config.json"), "w"),
        indent=4,
        sort_keys=True
        )

if __name__ == "__main__":
    main()
    print("Done.")
