#!/usr/local/bin/python

import os
import sqlite3
from bs4 import BeautifulSoup

DOCPATH = 'dart.docset/Contents/Resources/Documents'
DBPATH = 'dart.docset/Contents/Resources/docSet.dsidx'


def get_soup(path):
    with open(os.path.join(DOCPATH, path)) as f:
        page = f.read()

    return BeautifulSoup(page)


def insert(cursor, name, doc_type, path):
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, doc_type, path))
    print 'name: %s, type: %s, path: %s' % (name, 'Module', path)


def process_module(mod_path, cursor):
    soup = get_soup(mod_path)
    content = soup.find('div', {"class": "content"})
    functions = content.find_all('a', {"class": 'anchor-link'})
    classes = content.find_all('div', {"class": 'type'})

    for f in functions:
        link = '%s%s' % (mod_path, f.attrs['href'])
        name = f.parent.attrs['id']
        f_type = f.parent.parent.attrs['class'][0]
        insert(cur, name, f_type.capitalize(), link)

    for c in classes:
        class_link = c.find('a')
        link = class_link.attrs['href']
        name = class_link.text.strip()
        insert(cur, name, 'Class', link)
        yield link


def get_modules(cursor):
    soup = get_soup('index.html')

    nav_bar = soup.find('div', {"class": "nav"})
    for tag in nav_bar.find_all('a'):
        name = tag.text.strip()
        if len(name) > 0:
            path = tag.attrs['href'].strip()
            if path.split('#')[0] not in ('index.html', 'biblio.html', 'bookindex.html'):
                insert(cur, name, 'Module', path)
                yield path


if __name__ == '__main__':
    db = sqlite3.connect(DBPATH)
    cur = db.cursor()

    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    for mod_path in get_modules(cur):
        classes = list(process_module(mod_path, cur))
        for c in classes:
            process_module(c, cur)

    cur.execute("VACUUM ANALYZE;")
    db.commit()
    db.close()
