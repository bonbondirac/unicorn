'''
Created on 2012-6-28

@author: diracfang
'''

import unicorn
import urllib2
from readability.readability import Document
from BeautifulSoup import BeautifulSoup

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

def main():
    un = unicorn.Unicorn()
    url = raw_input('pls enter a url: ')
    print tell_url(un, url)
    

if __name__ == '__main__':
    main()
