'''
Created on 2012-6-28

@author: diracfang
'''

import unicorn
import urllib2
from readability.readability import Document
from BeautifulSoup import BeautifulSoup
import constants
import textwrap

def tell_url(un, url):
    buff = urllib2.urlopen(url)
    doc = Document(buff.read())
    html_buff = doc.summary()
    text_buff = extract_text(html_buff)
    class_name = un.tell_buff(text_buff)
    if class_name:
        class_name_human = un.get_class_name_human(class_name)
    else:
        class_name_human = None
    
    return class_name_human
    
def extract_text(html_buff):
    soup = BeautifulSoup(html_buff)
    all_text_list = []
    for tag in soup.findAll('p'):
        all_text_list.append(tag.text)
    all_text = '\n'.join(all_text_list)
    
    return all_text

def copy_db(un, host='localhost', port=6379, db=0):
    un.copy_db(host, port, db)
    
    return None

def dump_db(un, path):
    db_dump_string = un.dump_db()
    with open(path, 'wb') as f:
        f.write(db_dump_string)
    
    return len(db_dump_string)

def load_db(un, path):
    with open(path, 'rb') as f:
        db_dump_string = f.read()
    un.load_db(db_dump_string)
    
    return len(db_dump_string)
    

def main():
    un = unicorn.Unicorn()
    choice = raw_input(textwrap.dedent("""
    1) tell a url
    2) dump db
    3) load db
    4) copy db
    pls enter your choice: """))
    if choice == '1':
        url = raw_input('url: ')
        print tell_url(un, url)
    elif choice == '2':
        print '%d bytes dumped.' % dump_db(un, constants.DB_DUMP_PATH)
    elif choice == '3':
        print '%d bytes loaded.' % load_db(un, constants.DB_DUMP_PATH)
    elif choice == '4':
        host = raw_input('destination host: ')
        if host.strip() == '':
            host = 'localhost'
        port = raw_input('destination port: ')
        try:
            port = int(port)
        except:
            port = 6379
        db = raw_input('destination db: ')
        try:
            db = int(db)
        except:
            db = 2
        copy_db(un, host, port, db)
    

if __name__ == '__main__':
    main()
