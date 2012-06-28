'''
Created on 2012-6-28

@author: diracfang
'''

import os

BASE_PATH = os.path.abspath(__file__).replace('\\', '/')
TEXT_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                         'resource/SogouC.mini.20061102/Sample').replace('\\', '/')
CLASS_LIST_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                         'resource/SogouC.mini.20061102/ClassList.txt').replace('\\', '/')
COMMON_FREQ_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)),
                         'resource/SogouW/Freq/SogouLabDic.dic').replace('\\', '/')

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1

REDIS_PREFIX = 'un_'