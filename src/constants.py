'''
Created on 2012-6-28

@author: diracfang
'''

import os

BASE_PATH = os.path.abspath(__file__).replace('\\', '/')
TEXT_PATH_MINI = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                              'resource/SogouC.mini.20061102/Sample').replace('\\', '/')
TEXT_PATH_REDUCED = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                                 'resource/SogouC.reduced.20061102/Reduced').replace('\\', '/')
TEXT_PATH_FULL = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                                 'resource/SogouC/ClassFile').replace('\\', '/')
CLASS_LIST_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                               'resource/SogouC.mini.20061102/ClassList.txt').replace('\\', '/')
CLASS_WEIGHT_LIST_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                                      'resource/SogouC.mini.20061102/ClassWeightList.txt').replace('\\', '/')                         
COMMON_FREQ_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                                'resource/SogouW/Freq/SogouLabDic.dic').replace('\\', '/')
DB_DUMP_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                            'resource/unicorn_db.txt').replace('\\', '/')

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 2

REDIS_PREFIX = 'un_'

WORD_FREQ_KEY = 'freq:%s'
RARE_FREQ = 0.1
