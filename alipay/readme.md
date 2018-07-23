

## odoo11 支付宝接口模块开发

### 开发思路:

​	支付宝接口开发文档，规定了一些必选参数和非必选参数，详见[支付宝接口开发文档](https://docs.open.alipay.com/270/105898/)

![关键参数](./img/关键参数.png)![](./img/通知参数.png)

​	

​	支付宝在开发环境和生产环境下有不同的api，我们只需要在相应的url后面拼接正确的参数发起请求，就能跳转到支付宝的支付页面。

​	沙箱环境：https://openapi.alipaydev.com/gateway.do?

​	正式环境：https://openapi.alipay.com/gateway.do?

​	我们拼接的参数中有一个return_url，如果支付成功，支付宝会用重定向的方式跳转到return_url指定的页面，展示给用户。还有一个异步通知的参数notify_url ，支付成功，支付宝参数用post请求该页面，服务器修改订单状态，服务器收到支付宝的请求请求之后必须返回'success'，否则支付宝会每隔一段时间请求一次。

#### 公钥、私钥

​	我们请求支付宝的参数，都是通过RSA2算法加密过的。首先，我们要先在支付宝上申请一个app，支付宝审核过之后，会给我们该app的AppId。如果是沙箱环境，支付宝有提供测试app。我们需要用openssl工具生成app的公钥和私钥，app公钥上传支付宝，然后支付宝会给你一个支付宝公钥。

![](./img/沙箱应用.png)

​	**生成秘钥的方式：**

​	首先进入OpenSSL工具，输入以下命令。 

```
OpenSSL> genrsa -out app_private_key.pem   2048  #生成私钥
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem #生成公钥
OpenSSL> exit #退出OpenSSL程序
```

​	以上代码，会在当前目录生成app_private_key.pem（app RSA私钥，非Java语言适用）和app_public_key.pem（app RSA公钥）2个文件 。

​	私钥示例：

```
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQC+L0rfjLl3neHleNMOsYTW8r0QXZ5RVb2p/vvY3fJNNugvJ7lo4+fdBz+LN4mDxTz4MTOhi5e2yeAqx+v3nKpNmPzC5LmDjhHZURhwbqFtIpZD51mOfno2c3MDwlrsVi6mTypbNu4uaQzw/TOpwufSLWF7k6p2pLoVmmqJzQiD0QIDAQABAoGAakB1risquv9D4zX7hCv9MTFwGyKSfpJOYhkIjwKAik7wrNeeqFEbisqv35FpjGq3Q1oJpGkem4pxaLVEyZOHONefZ9MGVChT/MNH5b0FJYWl392RZy8KCdq376Vt4gKVlABvaV1DkapL+nLh7LMo/bENudARsxD55IGObMU19lkCQQDwHmzWPMHfc3kdY6AqiLrOss+MVIAhQqZOHhDe0aW2gZtwiWeYK1wB/fRxJ5esk1sScOWgzvCN/oGJLhU3kipHAkEAysNoSdG2oWADxlIt4W9kUiiiqNgimHGMHPwp4JMxupHMTm7D9XtGUIiDijZxunHv3kvktNfWj3Yji0661zHVJwJBAM8TDf077F4NsVc9AXVs8N0sq3xzqwQD/HPFzfq6hdR8tVY5yRMb4X7+SX4EDPORKKsgnYcur5lk8MUi7r072iUCQQC8xQvUne+fcdpRyrR4StJlQvucogwjTKMbYRBDygXkIlTJOIorgudFlrKP/HwJDoY4uQNl8gQJb/1LdrKwIe7FAkBl0TNtfodGrDXBHwBgtN/t3pyi+sz7OpJdUklKE7zMSBuLd1E3O4JMzvWP9wEE7JDb+brjgK4/cxxUHUTkk592
-----END RSA PRIVATE KEY-----
```

​	公钥示例：

```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQWiDVZ7XYxa4CQsZoB3n7bfxLDkeGKjyQPt2FUtm4TWX9OYrd523iw6UUqnQ+Evfw88JgRnhyXadp+vnPKP7unormYQAfsM/CxzrfMoVdtwSiGtIJB4pfyRXjA+KL8nIa2hdQy5nLfgPVGZN4WidfUY/QpkddCVXnZ4bAUaQjXQIDAQAB
-----END PUBLIC KEY-----
```

​	**我们的app公钥上传支付宝，要去掉 -----BEGIN PUBLIC KEY-----和-----END PUBLIC KEY-----标识，保存的支付宝公钥要加上这两个标识，否则在加密解密时会出错。**

​	![](./img/app公钥.png)



---

​	快速生成addons，payment_alipay是addon 名称，test是文件生成保存的目录

```shell
python odoo-bin scaffold payment_alipay test
```

​	在开发之前，我们要安装一下依赖库pycrypto

```shell
pip install pycrypto
```

###### \__manifest__.py

addon 配置

```shell
# -*- coding: utf-8 -*-

{
    'name': 'Alipay Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: Alipay Implementation',
    'version': '1.0',
    'description': """
Alipay Payment Acquirer，支付宝支付模块，用于支付宝即时收款功能.
需要安装pycrypto Python库，通过命令`pip install pycrypto`安装.
    """,
    'depends': ['payment'],
    'external_dependencies': {
        'python': ['Crypto'],
        'bin': [],
    },
    'data': [
        'views/payment_views.xml',
        'views/payment_alipay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
}
```

######models/payment.py

新建models/payment.py，继承payment.acquirer，添加支付支付的方式。

```python
# coding: utf-8

import json
import logging
import datetime
import time
import os
import urlparse
from urlparse import urljoin

import dateutil.parser
import pytz
from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', 'Alipay')], string='Provider',default='alipay', required=True)
    alipay_app_id = fields.Char('APP ID', groups='base.group_user')
    alipay_app_private_key = fields.Text('APP 私钥', groups='base.group_user')
    alipay_official_public_key = fields.Text('支付宝公钥', groups='base.group_user')
```

给开发环境和生成环境提供不同的接口

```python
@api.model
def _get_alipay_urls(self, environment):
    """ Alipay URLS """
    if environment == 'prod':
        return {
            'alipay_form_url': 'https://openapi.alipay.com/gateway.do?',
        }
    else:
        return {
            'alipay_form_url': 'https://openapi.alipaydev.com/gateway.do?',
        }
```

费用计算方式，参考官方payment_paypal

```python
@api.multi
def alipay_compute_fees(self, amount, currency_id, country_id):
    """ Compute Alipay fees.

        :param float amount: the amount to pay
        :param integer country_id: an ID of a res.country, or None. This is
                                   the customer's country, to be compared to
                                   the acquirer company country.
        :return float fees: computed fees
    """
    if not self.fees_active:
        return 0.0
    country = self.env['res.country'].browse(country_id)
    if country and self.company_id.country_id.id == country.id:
        #国内
        percentage = self.fees_dom_var
        fixed = self.fees_dom_fixed
    else:
        #国际
        percentage = self.fees_int_var
        fixed = self.fees_int_fixed
    fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
    return fees
```

根据当前是开发环境还是生产环境，选择相应的alipay_form_url

```python
@api.multi
def alipay_get_form_action_url(self):
    return self._get_alipay_urls(self.environment)['alipay_form_url']
```

现在我们可以考虑，生成传递给支付宝所必需的参数。我们需要先新建一个func.py的文件，写一个生成签名，验证签名，拼接url的方法。

###### models/func.py

```python
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

"""
 * 把字典所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串，并对字符串做urlencode编码
 * @param $para 需要拼接的数组
 * return 拼接完成以后的字符串
"""
def createLinkstringUrlencode(values):
    res = ""
    for k, v in values.iteritems():
        res += str(k) + "=" + quote_plus(str(v)) + "&"
    res = res[:-1]
    return res
```

拼接的字符串参数，需要去掉sign参数本身，另外要去掉空值的参数，所以要再定义一个筛选参数的方法。

```python
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
        if k not in ('sign', '') and v != '':
            prestr += '%s=%s&' % (k, v)
    prestr = prestr[:-1]
    return newparams, prestr
```

定义一个签名方法，用app私钥生成签名，返回签名结果

```python
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
```

用拼接好的参数生成签名

```python
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
```

验证签名

```python
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
```

###### #models/func.py完整版

```python
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
```

然后，我们再新建一个文件controllers/main.py，设置一下同步返回和异步返回的路由，以及处理逻辑

###### controllers/main.py

```python
# -*- coding: utf-8 -*-

import json
import logging
import pprint
import requests
import werkzeug
from werkzeug import urls

from odoo import http
from odoo.exceptions import ValidationError

from odoo.http import request

from test.payment_alipay.models import func

_logger = logging.getLogger(__name__)


class AlipayController(http.Controller):
    _notify_url = '/payment/alipay/ipn/'
    _return_url = '/payment/alipay/dpn/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from alipay. """
        return_url = post.pop('return_url', '')
        if not return_url:
            custom = json.loads(urls.url_unquote_plus(post.pop('custom', False) or post.pop('cm', False) or '{}'))
            return_url = custom.get('return_url', '/')
        return return_url
```

定义一个验证签名的方法

```python
"""
 * 获取返回时的签名验证结果
 * @param post 通知返回来的参数数组
 * @返回 签名验证结果
"""

def getSignVerify(self, **post):
    key_sorted = sorted(post.keys())
    content = ''
    sign_type = post['sign_type']
    sign = post['sign']
    charset = post['charset']

    for key in key_sorted:
        if key not in ["sign", "sign_type"]:
            if post[key]:
                content = content + key + "=" + post[key] + "&"
    content = content[:-1]
    content = content.encode(charset)
    alipay_official_public_key = request.env['payment.acquirer'].search([('provider', '=', 'alipay')],
                                                                        limit=1).alipay_official_public_key
    _logger.info(alipay_official_public_key)
    isSign = False
    if sign_type.upper() == "RSA2":
        isSign = func.rsaVerify(content, alipay_official_public_key, sign)
    return isSign
```

验证签名

```python
def verify_data(self, **post):
    if not post:
        return False
    else:
        isSign = self.getSignVerify(**post)
        if isSign:
            res = request.env['payment.transaction'].sudo().form_feedback(post, 'alipay')
            return True
        else:
            return False
```

异步通知处理

```python
@http.route('/payment/alipay/ipn/', type='http', auth="none", methods=['POST'], csrf=False)
def alipay_ipn(self, **post):
    """ Alipay IPN. """
    _logger.info('Beginning Alipay IPN form_feedback with post data %s', pprint.pformat(post))  # debug
    if self.verify_data(**post):
        return 'success'
    else:
        return 'fail'
```

同步通知处理

```python
@http.route('/payment/alipay/dpn', type='http', auth="none", methods=['POST', 'GET'], csrf=False)
def alipay_dpn(self, **post):
    """ Alipay RETURN """
    _logger.info('Beginning Alipay DPN form_feedback with post data %s', pprint.pformat(post))  # debug

    if self.verify_data(**post):
        return_url = self._get_return_url(**post)
        return werkzeug.utils.redirect(return_url)
    else:
        return "验签失败"
```

###### controllers/main.py完整版

```python
# -*- coding: utf-8 -*-

import json
import logging
import pprint
import requests
import werkzeug
from werkzeug import urls

from odoo import http
from odoo.exceptions import ValidationError

from odoo.http import request

from test.payment_alipay.models import func

_logger = logging.getLogger(__name__)


class AlipayController(http.Controller):
    _notify_url = '/payment/alipay/ipn/'
    _return_url = '/payment/alipay/dpn/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from alipay. """
        return_url = post.pop('return_url', '')
        if not return_url:
            custom = json.loads(urls.url_unquote_plus(post.pop('custom', False) or post.pop('cm', False) or '{}'))
            return_url = custom.get('return_url', '/')
        return return_url

    """
     * 获取返回时的签名验证结果
     * @param post 通知返回来的参数数组
     * @返回 签名验证结果
    """

    def getSignVerify(self, **post):
        key_sorted = sorted(post.keys())
        content = ''
        sign_type = post['sign_type']
        sign = post['sign']
        charset = post['charset']

        for key in key_sorted:
            if key not in ["sign", "sign_type"]:
                if post[key]:
                    content = content + key + "=" + post[key] + "&"
        content = content[:-1]
        content = content.encode(charset)
        alipay_official_public_key = request.env['payment.acquirer'].search([('provider', '=', 'alipay')],
                                                                            limit=1).alipay_official_public_key
        _logger.info(alipay_official_public_key)
        isSign = False
        if sign_type.upper() == "RSA2":
            isSign = func.rsaVerify(content, alipay_official_public_key, sign)
        return isSign

    def verify_data(self, **post):
        if not post:
            return False
        else:
            isSign = self.getSignVerify(**post)
            if isSign:
                res = request.env['payment.transaction'].sudo().form_feedback(post, 'alipay')
                return True
            else:
                return False

    @http.route('/payment/alipay/ipn/', type='http', auth="none", methods=['POST'], csrf=False)
    def alipay_ipn(self, **post):
        """ Alipay IPN. """
        _logger.info('Beginning Alipay IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        if self.verify_data(**post):
            return 'success'
        else:
            return 'fail'

    @http.route('/payment/alipay/dpn', type='http', auth="none", methods=['POST', 'GET'], csrf=False)
    def alipay_dpn(self, **post):
        """ Alipay RETURN """
        _logger.info('Beginning Alipay DPN form_feedback with post data %s', pprint.pformat(post))  # debug

        if self.verify_data(**post):
            return_url = self._get_return_url(**post)
            return werkzeug.utils.redirect(return_url)
        else:
            return "验签失败"
```

现在返回到models/payment.py，开始处理要给支付宝传递的参数。

先导一下包

```python
from test.payment_alipay.controllers.main import AlipayController
from test.payment_alipay.models import func
```

**这里有一个坑，发现不能从test目录导包，系统找不到这个路径，会报错。**这是因为test只是一个普通目录，我们要把它变成包，在test目录下新建一个文件\__init__.py，写入一下内容。

```python
import os
import sys

sys.path.append(os.getcwd())
```
` os.getcwd()`是获取当前目录，然后我们把当前目录加入到系统路径里。python在导包的时候，会先执行一些\__init__.py文件，然后在models/payment.py中就可以从test目录导包了。

现在返回到models/payment.py

```python
@api.multi
def alipay_form_generate_values(self, values):
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    # 公共参数
    alipay_tx_values = dict(values)
    alipay_tx_values.update({
        # basic parameters
        'method': 'alipay.trade.page.pay',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'return_url': '%s' % urljoin(base_url, AlipayController._return_url),
        'notify_url': '%s' % urljoin(base_url, AlipayController._notify_url),
        'app_id': self.alipay_app_id,
        'version': '1.0',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'biz_content': ''
    })

    _logger.info(alipay_tx_values)
    # 业务参数
    biz_content = {}
    # 商户订单号
    biz_content['out_trade_no'] = values['reference']
    biz_content['product_code'] = 'FAST_INSTANT_TRADE_PAY'
    biz_content['total_amount'] = values['amount']

    biz_content['subject'] = '%s: %s' % (self.company_id.name, values['reference'])
    biz_content['body'] = '%s: %s' % (self.company_id.name, values['reference'])

    alipay_tx_values.update({'biz_content': json.dumps(biz_content)})

    subkey = ['app_id', 'method', 'version', 'charset', 'sign_type', 'timestamp', 'biz_content', 'return_url',
              'notify_url']
    need_sign = {key: alipay_tx_values[key] for key in subkey}
    params, sign = func.buildRequestMysign(need_sign, self.alipay_app_private_key)
    alipay_tx_values.update({
        'sign': sign,
    })
    _logger.info('script_dir : %s' % (os.path.dirname(__file__)))
    return alipay_tx_values
```

到这里，我们就已经把支付宝要传递的参数就全都生成了，但是我们并没有看到之前去请求支付宝的方法，在我们继承的payment.acquirer中好像也没有。odoo应该是通过点击支付按钮，然后通过js发起get请求。

我们可以自己测试一下，在沙箱环境下用alipay_form_url 和处理过的参数拼接，然后在浏览器里去请求这个url，看看是否能够跳转到支付界面。

我们把上面的代码调整一下

```python
_logger.info('script_dir : %s' % (os.path.dirname(__file__)))

print('--------testing  start---------------')
need_sign.update({'sign': sign})
print(need_sign)
url = func.createLinkstringUrlencode(need_sign)
alipay_url = self.alipay_get_form_action_url() + url
print(alipay_url)
print('--------testing  end-----------------')
return alipay_tx_values
```

当我们在odoo的网站商城中，用alipay点击支付时，在控制台会打印一个alipay_url。

```python
class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('trade_no')
        if not reference or not txn_id:
            error_msg = _('Alipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _alipay_form_validate(self, data):

        res = {
            'acquirer_reference': data.get('out_trade_no'),
            'alipay_reference': data.get('trade_no'),
            'partner_reference': data.get('seller_id')
        }
        try:
            # dateutil and pytz don't recognize abbreviations PDT/PST
            tzinfos = {
                'PST': +8 * 3600,
                'PDT': +7 * 3600,
            }
            date_validate = dateutil.parser.parse(data.get('timestamp'), tzinfos=tzinfos).astimezone(pytz.utc)
        except:
            date_validate = fields.Datetime.now()
        res.update(state='done', date_validate=date_validate)
        return self.write(res)
```

这个继承payment.transaction，参考payment_paypal，具体方法没太看懂，看输出的话是支付完成更改订单状态。

###### models/payment.py完整版

```python
# coding: utf-8

import json
import logging
import datetime
import time
import os
import urlparse
from urlparse import urljoin

import dateutil.parser
import pytz
from werkzeug import urls

from odoo.tools.float_utils import float_compare
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from test.payment_alipay.controllers.main import AlipayController
from test.payment_alipay.models import func


_logger = logging.getLogger(__name__)


class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', 'Alipay')], string='Provider',
                                default='alipay', required=True)

    alipay_app_id = fields.Char('APP ID', groups='base.group_user')
    alipay_app_private_key = fields.Text('APP 私钥', groups='base.group_user')
    alipay_official_public_key = fields.Text('支付宝公钥', groups='base.group_user')

    @api.model
    def _get_alipay_urls(self, environment):
        """ Alipay URLS """
        if environment == 'prod':
            return {
                'alipay_form_url': 'https://openapi.alipay.com/gateway.do?',
            }
        else:
            return {
                'alipay_form_url': 'https://openapi.alipaydev.com/gateway.do?',
            }

    @api.multi
    def alipay_compute_fees(self, amount, currency_id, country_id):
        """ Compute Alipay fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            #国内
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            #国际
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def alipay_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # 公共参数
        alipay_tx_values = dict(values)
        alipay_tx_values.update({
            # basic parameters
            'method': 'alipay.trade.page.pay',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'return_url': '%s' % urljoin(base_url, AlipayController._return_url),
            'notify_url': '%s' % urljoin(base_url, AlipayController._notify_url),
            'app_id': self.alipay_app_id,
            'version': '1.0',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'biz_content': ''
        })

        _logger.info(alipay_tx_values)
        # 业务参数
        biz_content = {}
        # 商户订单号
        biz_content['out_trade_no'] = values['reference']
        biz_content['product_code'] = 'FAST_INSTANT_TRADE_PAY'
        biz_content['total_amount'] = values['amount']

        biz_content['subject'] = '%s: %s' % (self.company_id.name, values['reference'])
        biz_content['body'] = '%s: %s' % (self.company_id.name, values['reference'])

        # alipay_tx_values.update({'biz_content':biz_content_sign.decode('utf-8')})
        alipay_tx_values.update({'biz_content': json.dumps(biz_content)})

        subkey = ['app_id', 'method', 'version', 'charset', 'sign_type', 'timestamp', 'biz_content', 'return_url',
                  'notify_url']
        need_sign = {key: alipay_tx_values[key] for key in subkey}
        params, sign = func.buildRequestMysign(need_sign, self.alipay_app_private_key)
        alipay_tx_values.update({
            'sign': sign,
        })
        _logger.info('script_dir : %s' % (os.path.dirname(__file__)))

        print('--------testing  start---------------')
        need_sign.update({'sign': sign})
        print(need_sign)
        url = func.createLinkstringUrlencode(need_sign)
        alipay_url = self.alipay_get_form_action_url() + url
        print(alipay_url)
        print('--------testing  end-----------------')
        '''
        get请求指定参数+签名,就能跳转支付界面
        '''
        return alipay_tx_values

    @api.multi
    def alipay_get_form_action_url(self):
        return self._get_alipay_urls(self.environment)['alipay_form_url']


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('trade_no')
        if not reference or not txn_id:
            error_msg = _('Alipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _alipay_form_validate(self, data):

        res = {
            'acquirer_reference': data.get('out_trade_no'),
            'alipay_reference': data.get('trade_no'),
            'partner_reference': data.get('seller_id')
        }
        try:
            # dateutil and pytz don't recognize abbreviations PDT/PST
            tzinfos = {
                'PST': +8 * 3600,
                'PDT': +7 * 3600,
            }
            date_validate = dateutil.parser.parse(data.get('timestamp'), tzinfos=tzinfos).astimezone(pytz.utc)
        except:
            date_validate = fields.Datetime.now()
        res.update(state='done', date_validate=date_validate)
        return self.write(res)
```

再写一下视图

###### views/payment_views.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="acquirer_form_alipay" model="ir.ui.view">
            <field name="name">acquirer.form.alipay</field>
            <field name="model">payment.acquirer</field>
            <field name="inherit_id" ref="payment.acquirer_form"/>
            <field name="arch" type="xml">
                <xpath expr='//group[@name="acquirer"]' position='after'>
                    <group class="alipay_css" attrs="{'invisible': [('provider', '!=', 'alipay')]}">
                        <field name="alipay_app_id"/>
                        <field name="alipay_app_private_key"/>
                        <field name="alipay_official_public_key"/>
                        <a colspan="2" href="https://www.alipay.com/" target="_blank">How to configure your alipay
                            account?
                        </a>
                    </group>
                </xpath>
            </field>
        </record>

        <record id="transaction_form_alipay" model="ir.ui.view">
            <field name="name">acquirer.transaction.form.alipay</field>
            <field name="model">payment.transaction</field>
            <field name="inherit_id" ref="payment.transaction_form"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='acquirer_reference']" position="after">
                    <field name="alipay_txn_type" readonly="1" attrs="{'invisible': [('provider', '!=', 'alipay')]}"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
```

###### views/payment_alipay_templates.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <template id="alipay_form">
            <div>
                <input type="hidden" name="data_set" t-att-data-action-url="tx_url" data-remove-me=""/>
                <input type="hidden" name="app_id" t-att-value="app_id"/>
                <input type="hidden" name="method" t-att-value="method"/>
                <input type="hidden" name="version" t-att-value="version"/>
                <input type="hidden" name="notify_url" t-att-value="notify_url"/>
                <input type="hidden" name="return_url" t-att-value="return_url"/>
                <input type="hidden" name="charset" t-att-value="charset"/>
                <input type="hidden" name="timestamp" t-att-value="timestamp"/>
                <input type="hidden" name="sign_type" t-att-value="sign_type"/>
                <input type="hidden" name="biz_content" t-att-value="biz_content"/>
                <input type="hidden" name="sign" t-att-value="sign" />               
            </div>
        </template>
    </data>
</odoo>
```

在data里新建payment_acquirer_data.xml，写入预设数据。

###### data/payment_acquirer_data.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <record id="payment.payment_acquirer_alipay" model="payment.acquirer">
            <field name="name">Alipay</field>
            <field name="image" type="base64" file="payment_alipay/static/src/img/alipay_logo.png"/>
            <field name="provider">alipay</field>
            <field name="company_id" ref="base.main_company"/>
            <field name="view_template_id" ref="alipay_form"/>
            <field name="environment">prod</field>
            <field name="pre_msg"><![CDATA[<p>You will be redirected to the Alipay website after clicking on the payment button.</p>]]></field>
            
            <field name="alipay_app_id"></field>
            <field name="alipay_app_private_key"></field>
            <field name="alipay_official_public_key"></field>
        </record>

    </data>
</odoo>
```

在odoo里更新应用列表，选择payment_alipay模块安装。

然后在开票的配置中，选择收单，点击进入之后选择Alipay进行设置。输入app ID，app私钥，支付宝公钥保存。

![](./img/收单.png)

![](./img/ailpay配置.png)

在输入app私钥，支付宝公钥时，一定要带上标识。

![](./img/alipay配置2.png)

左边的按钮可以切换测试和生产环境，右边的按钮只有切换到已发布，在支付的界面才有alipay的选项。

都配置好之后，我们可以测试一下支付宝支付的方式能不能用，点到网站的商城里，把商品加入购物车。

![](./img/购物车.png)

点击结账流程，确认收货地址。

![](./img/确认收货地址.png)

支付方式选择Alipay，点击付款

![](C:\Users\mango.li\Desktop\笔记\alipay\img\付款.png)

如果没有出错的话，现在应该跳转到了扫码支付的界面。

![](C:\Users\mango.li\Desktop\笔记\alipay\img\扫描支付.png)

点击右边的登录账户付款，用支付宝给我们的测试账号进行登录。

![](./img/支付.png)

然后，输入密码进行支付。

![](./img/支付成功.png)

支付成功3秒后，会跳转到我们return_url指定的页面。
