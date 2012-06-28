'''
Created on 2012-6-28

@author: diracfang
'''

import os
import constants
import redis
import helper
from smallseg.smallseg import SEG

class Unicorn(object):
    
    def __init__(self):
        self._class_dict = dict()
        self._freq_dict = dict()
        self._redis_instance = redis.StrictRedis(host=constants.REDIS_HOST,
                                                 port=constants.REDIS_PORT,
                                                 db=constants.REDIS_DB)
        self.seg = SEG()
        self._load_class_dict(constants.CLASS_LIST_PATH)
        self._load_common_freq(constants.COMMON_FREQ_PATH)
    
    def _load_class_dict(self, path):
        print 'loading class dict...',
        with open(path, 'rb') as f:
            for line in f:
                line = line.strip()
                class_name, alias = line.split()
                self._class_dict[class_name] = helper.unicodefy(alias)
        print 'done!'
        
        return None
    
    def _load_common_freq(self, path):
        print 'loading word freq...',
        with open(path, 'rb') as f:
            for line in f:
                line = line.strip()
                line_parts = line.split()
                if len(line_parts) == 3:
                    word, freq, cls = line_parts
                else:
                    word, freq = line_parts
                    cls = None
                try:
                    word = word.decode('gbk')
                except:
                    pass
                else:
                    self._freq_dict[word] = freq
        print 'done!'
    
    def feed_multi_text(self, path):
        self.parse_path(path, callback=self.feed_single_text)
        
    def feed_single_text(self, class_name, path):
        with open(path, 'rb') as f:
            content = f.read()
        content = helper.unicodefy(content)
        words = self.seg.cut(content)
        for word in words:
            
        
        
    
    def parse_path(self, path, callback=None):
        for dirpath, dirnames, filenames in os.walk(os.path.abspath(path)):
            if dirnames == []:
                class_name = dirpath.replace('\\', '/').split('/')[-1]
                paths = [os.path.join(dirpath, filename).replace('\\', '/') for filename in filenames]
                if callback:
                    for path in paths:
                        callback(class_name, path)
                        break
                break

    
def main():
    un= Unicorn()
    un.feed_multi_text(constants.TEXT_PATH)


if __name__ == '__main__':
    main()