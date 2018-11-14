# coding: utf-8

import json
import sys
import types
import logging
import hashlib

# pip install pycrypto 安装pycrypto库
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

from base64 import b64encode, b64decode
from urllib import urlencode,quote_plus

_logger = logging.getLogger(__name__)


# def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
#     if strings_only and isinstance(s, (types.NoneType, int)):
#         return s
#     if not isinstance(s, str):
#         try:
#             return str(s)
#         except UnicodeEncodeError:
#             if isinstance(s, Exception):
#                 return ' '.join([smart_str(arg, encoding, strings_only,
#                                            errors) for arg in s])
#             return unicode(s).encode(encoding, errors)
#     elif isinstance(s, str):
#         return s.encode(encoding, errors)
#     elif s and encoding != 'utf-8':
#         return s.decode('utf-8', errors).encode(encoding, errors)
#     else:
#         return s


"""
 * 除去数组中的空值和签名参数
 * @param  签名参数组
 * return 去掉空值与签名参数后的新签名参数组
"""


def params_filter(params):
    ks = sorted(params)
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        # k = smart_str(k)
        if k not in ('sign', '') and v != '':
            # newparams[k] = smart_str(v)
            prestr += '%s=%s&' % (k, v)
    prestr = prestr[:-1]
    return newparams, prestr


"""
 * 把数组所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串
 * @param $para 需要拼接的数组
 * return 拼接完成以后的字符串
  函数没有用到，先放着
"""


def createLinkstring(values):
    res = ""
    for k, v in values.iteritems():
        res += str(k) + "=" + str(v) + "&"
    res = res[:-1]
    return res


"""
 * 把所有字典元素，按照“参数=参数值”的模式用“&”字符拼接成字符串，并对字符串做urlencode编码
 * @param $para 需要拼接的数组
 * return 拼接完成以后的字符串
"""


def createLinkstringUrlencode(values):
    res = ""
    for k, v in values.iteritems():
        res += str(k) + "=" + quote_plus(str(v)) + "&"
    res = res[:-1]
    return res

"""
 * RSA签名
 * @param data 待签名数据
 * @param private_key 商户私钥字符串
 * return 签名结果
"""


def rsaSign(data, private_key):
    key = RSA.importKey(private_key)
    hash_obj = SHA256.new(data.encode())
    signer = PKCS1_v1_5.new(key)
    d = b64encode(signer.sign(hash_obj))
    return d


"""
*生成签名结果
*param $para_sort 已排序要签名的数组
* return 签名结果字符串
"""


def buildRequestMysign(values, private_key):
    # 把数组所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串
    params, prestr = params_filter(values)
    _logger.info('Sign Str : %s' % (prestr))
    mysign = rsaSign(prestr, private_key) or ''
    return params, mysign


"""
 * RSA验签
 * @param $data 待签名数据
 * @param $public_key 支付宝的公钥字符串
 * @param $sign 要校对的的签名结果
 * return 验证结果
"""


def rsaVerify(data, public_key, sign):
    _logger.info(public_key)
    rsakey = RSA.importKey(public_key)
    res = SHA256.new(data)
    verifier = PKCS1_v1_5.new(rsakey)
    return verifier.verify(res, b64decode(sign))

#
# def aesEncrypt(data, key):
#     bs = 16
#     IV = 16 * '\x00'
#     mode = AES.MODE_CBC
#     # aes_key = hashlib.sha256(key.encode()).digest()
#     cipher = AES.new(b64decode(key), mode, IV=IV)
#     return b64encode(cipher.encrypt(pad(data, bs)))
#
#
# def pad(s, bs):
#     return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
