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
        self._parse_path(path, callback=self.feed_single_text)
        
    def feed_single_text(self, class_name, path):
        with open(path, 'rb') as f:
            content = f.read()
        content = helper.unicodefy(content)
        words = self.seg.cut(content)
        for word in words:
            self._incr_freq_count(class_name, word)
    
    def _generate_word_key(self, word):
        word_key = constants.WORD_FREQ_KEY % helper.unicode2utf8(word)
        
        return word_key
    
    def _generate_class_name_key(self, class_name):
        class_name_key = constants.REDIS_PREFIX + class_name
        
        return class_name_key
    
    def _incr_freq_count(self, class_name, word, delta=1):
        class_name_key = self._generate_class_name_key(class_name)
        word_key = self._generate_word_key(word)
        freq = self._redis_instance.hget(class_name_key, word_key)
        if freq:
            freq = str(long(freq) + delta)
        else:
            freq = '1'
        self._redis_instance.hset(class_name_key, word_key, freq)
        
        return None
    
    def _get_freqs_dict_by_class(self, class_name, words):
        words = list(set(words))
        freqs_dict = dict()
        class_name_key = self._generate_class_name_key(class_name)
        word_keys = [self._generate_word_key(word) for word in words]
        freqs = self._redis_instance.hmget(class_name_key, word_keys)
        # this constants.RARE_FREQ depends on training material
        freqs = [int(freq) if freq else constants.RARE_FREQ for freq in freqs]
        for kv in zip(word_keys, freqs):
            freqs_dict[kv[0]] = kv[1] 
        
        return freqs_dict
    
    def _get_freq_in_dict(self, freqs_dict, word):
        word_key = self._generate_word_key(word)
        freq_str = freqs_dict.get(word_key, None)
        freq = float(freq_str) if freq_str else constants.RARE_FREQ
        
        return freq
    
    def _parse_path(self, path, callback=None):
        for dirpath, dirnames, filenames in os.walk(os.path.abspath(path)):
            if dirnames == []:
                class_name = dirpath.replace('\\', '/').split('/')[-1]
                paths = [os.path.join(dirpath, filename).replace('\\', '/') for filename in filenames]
                if callback:
                    for path in paths:
                        print 'feeding %s' % path,
                        callback(class_name, path)
                        print 'done!'
    
    def tell_file(self, path):
        with open(path, 'rb') as f:
            content = f.read()
            
        return self.tell_buff(content)
    
    def tell_buff(self, buff):
        words = self.seg.cut(buff)
        for class_name in self._class_dict:
            freqs_dict = self._get_freqs_dict_by_class(class_name, words)
            multi_freq = 1
            for word in words:
                multi_freq *= self._get_freq_in_dict(freqs_dict, word)
            print class_name, multi_freq
            
        
    def clear_db(self):
        print 'clear db...',
        self._redis_instance.flushdb()
        print 'done!'
        
        return None

    
def main():
    un= Unicorn()
    un.clear_db()
    un.feed_multi_text(constants.TEXT_PATH)
    f = 'C:/Users/diracfang/Documents/workspace/unicorn/resource/SogouC.mini.20061102/Sample/C000007/10.txt'
    un.tell_file(f)


if __name__ == '__main__':
    main()
