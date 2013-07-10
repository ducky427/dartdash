
import os
import sqlite3
from bs4 import BeautifulSoup

DOCPATH = 'dart.docset/Contents/Resources/Documents'
DBPATH = 'dart.docset/Contents/Resources/docSet.dsidx'

DASH_TYPES = {
    'Functions': 'Function',
    'Constructors': 'Function',
    'Properties': 'Property',
    'Methods': 'Method',
    'Opertors': 'Operator',
    'Abstract Classes': 'Class',
    'Classes': 'Class',
    'Typedefs': 'Type',
    'Exceptions': 'Exception',
    'Operators': 'Operator'
}


ANCHOR_TYPES = ['Functions', 'Constructors', 'Properties', 'Methods', 'Operators']
TYPE_TYPES = ['Abstract Classes', 'Classes', 'Typedefs', 'Exceptions']
ALL_TYPES = ANCHOR_TYPES + TYPE_TYPES


def get_soup(path):
    with open(os.path.join(DOCPATH, path)) as f:
        page = f.read()

    return BeautifulSoup(page)


def insert(cursor, name, doc_type, path):
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, doc_type, path))
    print 'name: %s, type: %s, path: %s' % (name, 'Module', path)


def parse_anchor_type(mod_path, parent):
    links = parent.find_all('a', {"class": 'anchor-link'})
    for f in links:
        link = '%s%s' % (mod_path, f.attrs['href'])
        name = f.parent.attrs['id']
        yield link, "%s.%s" % (mod_path.replace('_', '.').replace('/', '.')[:-5], name)


def parse_type_type(mod_path, parent):
    links = parent.find_all('div', {"class": 'type'})
    for c in links:
        class_link = c.find('a')
        link = class_link.attrs['href']
        name = class_link.text.strip()
        yield link, name


def process_module(mod_path, cursor):
    soup = get_soup(mod_path)
    children = []
    for tag in soup.find_all('h3'):
        if tag.text not in ALL_TYPES:
            print "ignoring: %s" % tag.text
            continue
        parent = tag.parent

        gen = None
        to_return = False
        if tag.text in ANCHOR_TYPES:
            gen = parse_anchor_type(mod_path, parent)
        else:
            gen = parse_type_type(mod_path, parent)
            to_return = True

        for link, name in gen:
            insert(cursor, name, DASH_TYPES[tag.text], link)
            if to_return:
                children.append(link)
    return children


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
        children = process_module(mod_path, cur)
        for c in children:
            process_module(c, cur)

    cur.execute("VACUUM ANALYZE;")
    db.commit()
    db.close()
