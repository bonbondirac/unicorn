'''
Created on 2012-6-28

@author: diracfang
'''

import chardet

def unicodefy(buff):
    """
    return an unicode representation of the string buff,
    ignore any error
    """
    if isinstance(buff, unicode):
        return buff
    else:
        guessed_encoding = chardet.detect(buff)['encoding']
        try:
            unicode_str_buffer = unicode(buff, guessed_encoding, 'ignore')
        except:
            unicode_str_buffer = unicode()
        return unicode_str_buffer
    
def unicode2utf8(buff):
    if not isinstance(buff, unicode):
        buff = unicodefy(buff)
    
    try:
        str_buff = buff.encode('utf-8')
    except:
        str_buff = ''
    
    return str_buff
