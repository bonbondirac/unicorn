'''
Created on 2012-6-28

@author: diracfang
'''

import os
import constants
import redis
import helper
import math
from smallseg.smallseg import SEG
import anyjson

class Unicorn(object):
    
    def __init__(self):
        self._class_dict = dict()
        self._class_weight_dict = dict()
        self._freq_dict = dict()
        self._redis_instance = redis.StrictRedis(host=constants.REDIS_HOST,
                                                 port=constants.REDIS_PORT,
                                                 db=constants.REDIS_DB)
        self._load_seg_dict()
        self._load_class_dict(constants.CLASS_LIST_PATH)
        self._load_class_weight_dict(constants.CLASS_WEIGHT_LIST_PATH)
        self._load_common_freq(constants.COMMON_FREQ_PATH)
    
    def _cut_text(self, buff):
        buff = helper.unicodefy(buff)
        words = self._seg.cut(buff)
        words = self._filter_words(words)
#        words = list(set(words))
        
        return words
    
    def _filter_words(self, words):
        new_words = []
        for word in words:
            if self._is_valid_word(word):
                new_words.append(word)
        
        return new_words
    
    def _is_valid_word(self, buff):
        if self._is_word_len_enough(buff) and self._is_word_not_number(buff):
            return True
        else:
            return False
    
    def _is_word_len_enough(self, buff):
        if len(buff) >= 2:
            return True 
        else:
            return False
    
    def _is_word_not_number(self, buff):
        if not buff.isnumeric():
            return True
        else:
            return False
    
    def _load_seg_dict(self):
        print 'loading seg dict...',
        self._seg = SEG()
        print 'done!'
        
        return None
    
    def _load_class_dict(self, path):
        print 'loading class dict...',
        with open(path, 'rb') as f:
            for line in f:
                line = line.strip()
                class_name, alias = line.split()
#                self._class_dict[class_name] = helper.unicodefy(alias)
                self._class_dict[class_name] = alias.decode('gbk')
        print 'done!'
        
        return None
    
    def _load_class_weight_dict(self, path):
        print 'loading class weight dict...',
        with open(path, 'rb') as f:
            for line in f:
                line = line.strip()
                class_name, weight = line.split()
                self._class_weight_dict[class_name] = float(weight)
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
                    self._freq_dict[word] = int(freq)
        print 'done!'
        
        return None
    
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
        if word_keys:
            freqs = self._redis_instance.hmget(class_name_key, word_keys)
#            this constants.RARE_FREQ depends on training material
            freqs = [int(freq) if freq else constants.RARE_FREQ for freq in freqs]
            for kv in zip(word_keys, freqs):
                freqs_dict[kv[0]] = kv[1] 
        
        return freqs_dict
    
    def _get_factor_in_dict(self, freqs_dict, word):
        word_key = self._generate_word_key(word)
        freq_str = freqs_dict.get(word_key, None)
        freq = float(freq_str) if freq_str else constants.RARE_FREQ
        
        return freq
    
    def _get_factors_in_dict(self, freqs_dict, words):
        factors = []
        for word in words:
            factors.append(self._get_factor_in_dict(freqs_dict, word))
        
        return factors
    
    def _factors_to_product(self, factors_dict, words):
        ln_product_dict = dict()
        if factors_dict:
            factor_count = len(factors_dict.values()[0])
            keys = factors_dict.keys()
            for i in range(factor_count):
#                print words[i]
                for key in keys:
                    old_ln_product = ln_product_dict.get(key, None)
                    ln_factor = math.log(factors_dict[key][i]) 
                    if old_ln_product:
                        ln_product_dict[key] += ln_factor
                    else:
#                        starting by a base factor of 1
                        ln_product_dict[key] = ln_factor
#                    print self._class_dict[key], ln_product_dict[key], ' | ',
#                print
#                print words[i], ln_product_dict
                    
        return ln_product_dict
    
    def _normalize_product_dict(self, product_dict):
        total = sum(product_dict.values())
        for key in product_dict:
            value = product_dict[key]
            value /=  total
            product_dict[key] = int(value * 1000 + 0.5) / 1000.0
        
        return product_dict
    
    def _cmp_class_result_list(self, x, y):
        if x[1] < y[1]:
            return -1
        elif x[1] == y[1]:
            return 0
        else:
            return 1
    
    def _parse_path(self, path, callback=None):
        for dirpath, dirnames, filenames in os.walk(os.path.abspath(path)):
            if dirnames == []:
                class_name = dirpath.replace('\\', '/').split('/')[-1]
                paths = [os.path.join(dirpath, filename).replace('\\', '/') for filename in filenames if filename.endswith('.txt')]
                if callback:
                    for path in paths:
                        print 'feeding %s ...' % path,
                        callback(class_name, path)
                        print 'done!'
        
        return None
    
    def feed_single_text(self, class_name, path):
        with open(path, 'rb') as f:
            content = f.read()
        words = self._cut_text(content)
        for word in words:
            self._incr_freq_count(class_name, word)
        
        return None
    
    def feed_multi_text(self, path):
        self._parse_path(path, callback=self.feed_single_text)
        
        return None
    
    def tell_buff(self, buff):
        words = self._cut_text(buff)
        factors_dict = dict()
        for class_name in self._class_dict:
            freqs_dict = self._get_freqs_dict_by_class(class_name, words)
            factors_dict[class_name] = self._get_factors_in_dict(freqs_dict, words)
        product_dict = self._factors_to_product(factors_dict, words)
        product_dict = self._add_class_weight(product_dict)
#        product_dict = self._normalize_product_dict(product_dict)
        class_result_list = product_dict.items()
        class_result_list = sorted(class_result_list,
                                   cmp=self._cmp_class_result_list,
                                   reverse=True)
#        class_result_list = [(self._class_dict[k], v) for k, v in class_result_list]
#        for i, j in class_result_list:
#            print i, j, ' | ',
#        print
        if class_result_list:
            first_result = class_result_list[0][0]
        else:
            first_result = None
#        print first_result
        
        return first_result
    
    def _add_class_weight(self, product_dict):
        for class_name in self._class_dict:
            if product_dict.has_key(class_name):
                product_dict[class_name] *= self._class_weight_dict[class_name]
        
        return product_dict
    
    def _get_db_keys(self):
        keys = self._redis_instance.keys(constants.REDIS_PREFIX + '*')
        
        return keys
    
    def tell_file(self, path):
        with open(path, 'rb') as f:
            content = f.read()
            
        return self.tell_buff(content)
    
    def clear_db(self):
        print 'clear db...',
        keys = self._get_db_keys()
        if keys:
            self._redis_instance.delete(*keys)
        print 'done!'
        
        return None
    
    def get_class_name_human(self, class_name):
        
        return self._class_dict[class_name]
    
    def copy_db(self, des_host, des_port, des_db):
        print 'moving db...',
        des_redis_instance = redis.StrictRedis(host=des_host, port=des_port, db=des_db)
        keys = self._get_db_keys()
        src_pipe = self._redis_instance.pipeline(transaction=True)
        for key in keys:
            src_pipe.hgetall(key)
        mappings = src_pipe.execute()
        des_pipe = des_redis_instance.pipeline(transaction=True)
        for key, mapping in zip(keys, mappings):
            des_pipe.hmset(key, mapping)
        des_pipe.execute()
        print 'done!'
        
        return None
    
    def dump_db(self):
        print 'dumping db...',
        db_data = dict()
        keys = self._get_db_keys()
        pipe = self._redis_instance.pipeline(transaction=True)
        for key in keys:
            pipe.hgetall(key)
        mappings = pipe.execute()
        for key, mapping in zip(keys, mappings):
            db_data[key] = mapping
        db_dump_string = anyjson.dumps(db_data)
        print 'done!'
        
        return db_dump_string
    
    def load_db(self, db_dump_string):
        print 'loading db...',
        db_data = anyjson.loads(db_dump_string)
        pipe = self._redis_instance.pipeline(transaction=True)
        for key in db_data:
            pipe.hmset(key, db_data[key])
        pipe.execute()
        print 'done!'
        
        return None


def main():
    un= Unicorn()
    un.clear_db()
    un.feed_multi_text(constants.TEXT_PATH_FULL)
    fs = []
#    path = 'C:/Users/diracfang/Documents/workspace/unicorn/resource/SogouC.mini.20061102/Sample'
    path = constants.TEXT_PATH_MINI
    for dirpath, dirnames, filenames in os.walk(os.path.abspath(path)):
            if dirnames == []:
                fs.extend([os.path.join(dirpath, filename).replace('\\', '/') for filename in filenames if filename.endswith('.txt')])
    counter = 0
    valid_counter = 0
#    fs = ['c:/test.txt']
    for f in fs:
        result = un.tell_file(f)
        if result:
#            print un.get_class_name_human(result)
#            print result, f.split('/')[-2]
            if result == f.split('/')[-2]:
                valid_counter += 1
        counter += 1
        print 'accuracy: %d/%d' % (valid_counter, counter)
    print 'overall accuracy: %f' % (float(valid_counter) / counter)


if __name__ == '__main__':
    main()
