# -*- coding: utf-8 -*-
import math
import os
import json
import re
from bs4 import BeautifulSoup
from odoo import http
from odoo.http import local_redirect
from odoo.addons.website.controllers.main import Website

from ..models.func import paginator
from .uploader import Uploader
from ..config import Config
from ..models.models import Category


class News(http.Controller):
    # 分页
    def _get_pages(self, news_list, **kw):
        '''
                :param offset: 分页数量
                :param news_num:每页新闻数量
                :param total:总页数
                :return:
                '''
        offset = 3
        news_num = 5
        total = int(math.ceil(float(len(news_list)) / news_num))
        page = int(kw.get('page') or 1)
        if page <= 0 or page > total:
            page = 1
        prev = page - 1 if page > 1 else 1
        next = page + 1 if page < total else total
        start, end = paginator(page, offset, total)
        page_range = range(start, end)
        news_list = news_list[(page - 1) * news_num:page * news_num]
        page_data = {'page': page,
                     'prev': prev,
                     'next': next,
                     'page_range': page_range}
        return news_list, page_data

    # 去html标签
    def _del_html(self, news_list):
        news = []
        for new in news_list:
            new_dic = {}
            new_dic['id'] = new.id
            new_dic['title'] = new.title
            new_dic['content'] = BeautifulSoup(new.content, 'lxml').get_text()
            news.append(new_dic)
        return news

    @http.route('/news/add/', auth='user', methods=['GET', 'POST'])
    def news_add(self, **kw):
        req = http.request.httprequest
        message = None
        categories = http.request.env['news.category'].search([])
        if req.method == 'POST':
            print(req.values)
            content = req.values.get('editorValue')
            title = req.form.get('title')
            category = req.values.get('category', None)
            print(category)
            if content and title and category != u'选择':
                data = {
                    'category': category,
                    'title': title,
                    'content': content,
                }
                env = http.request.env()
                env['news.news'].sudo().create(data)
                message = {'msg': '发布成功！'}
                return local_redirect('/news/index', message)
            else:
                message = {'msg': '输入内容不能为空'}
                return http.request.render('news.add', message)

        data = {'categories': categories,
                }
        return http.request.render('news.add', data)

    @http.route('/news/index', auth='public')
    def index(self, **kw):
        news_list = http.request.env['news.news'].search([('is_delete', '=', False)]).order_by('-pub_time')
        news_list, page_data = self._get_pages(news_list, **kw)
        categories = http.request.env['news.category'].search([])
        news = self._del_html(news_list)

        data = {
            'news': news,
            'categories': categories,
            'msg': kw.get('msg'),
        }
        data.update(page_data)
        return http.request.render('news.index', data)

    @http.route('/news/detail/<int:id>/', auth='public', methods=['GET'])
    def detail(self, id):
        new = http.request.env['news.news'].browse(id)
        current_url = http.request.httprequest.base_url
        categories = http.request.env['news.category'].search([])
        data = {'new': new,
                'current_url': current_url,
                'categories': categories
                }
        return http.request.render('news.detail', data)

    @http.route('/news/change/<int:id>/', auth='user', methods=['GET', 'POST'])
    def change(self, id, **kw):
        new = http.request.env['news.news'].browse(id)
        req = http.request.httprequest
        current_url = req.base_url
        categories = http.request.env['news.category'].search([])
        data = {
            'new': new,
            'categories': categories,
            'current_url': current_url,
            'msg': None}
        if req.method == 'POST':
            title = req.form.get('title')
            category = req.form.get('category')
            content = req.values.get('editorValue')
            if title and content and category != u'选择':
                new.write({'title': title,
                           'content': content,
                           'category': category})
                message = '修改成功!'
            else:
                message = '输入内容不能为空!'
            data['msg'] = message
            return local_redirect('/news/detail/%s' % id)
        return http.request.render('news.change', data)

    @http.route('/news/delete/<int:id>', auth='user')
    def delete(self, id, **kw):
        new = http.request.env['news.news'].browse(id)
        current_url = http.request.httprequest.base_url
        message = None
        if http.request.httprequest.method == 'POST':
            new.write({'is_delete': True})
            message = '删除成功！'
            return local_redirect('/news/index', {'msg': message})
        data = {'new': new,
                'current_url': current_url,
                'msg': message}
        return http.request.render('news.delete', data)

    @http.route('/news/search', auth='public', methods=['GET'])
    def search(self, **kw):
        req = http.request.httprequest
        keyword = req.values.get('keyword', None)
        if keyword:
            news_list = http.request.env['news.news'].search(['|', ('title', 'like', keyword),
                                                              ('content', 'like', keyword)]).order_by('-pub_time')
            message = '总共找到%d条记录：' % len(news_list)
            categories = http.request.env['news.category'].search([])

            news_list, page_data = self._get_pages(news_list, **kw)
            news = self._del_html(news_list)
            data = {'news': news,
                    'categories': categories,
                    'msg': message,
                    'keyword': keyword
                    }
            data.update(page_data)
            return http.request.render('news.index', data)
        return local_redirect('/news/index')

    @http.route('/news/upload/', auth='public', csrf=False, methods=['GET', 'POST', 'OPTIONS'])
    def upload(self, **kw):
        """UEditor文件上传接口
           config 配置文件
           result 返回结果
           """
        mimetype = 'application/json'
        result = {}
        action = http.request.httprequest.args.get('action')

        # 解析JSON格式的配置文件
        with open(os.path.join(Config.STATIC_FOLDER, 'ueditor', 'php',
                               'config.json')) as fp:
            try:
                # 删除 `/**/` 之间的注释
                CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
            except:
                CONFIG = {}

        if action == 'config':
            # 初始化时，返回配置文件给客户端
            result = CONFIG

        elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
            # 图片、文件、视频上传
            if action == 'uploadimage':
                fieldName = CONFIG.get('imageFieldName')
                config = {
                    "pathFormat": CONFIG['imagePathFormat'],
                    "maxSize": CONFIG['imageMaxSize'],
                    "allowFiles": CONFIG['imageAllowFiles']
                }
            elif action == 'uploadvideo':
                fieldName = CONFIG.get('videoFieldName')
                config = {
                    "pathFormat": CONFIG['videoPathFormat'],
                    "maxSize": CONFIG['videoMaxSize'],
                    "allowFiles": CONFIG['videoAllowFiles']
                }
            else:
                fieldName = CONFIG.get('fileFieldName')
                config = {
                    "pathFormat": CONFIG['filePathFormat'],
                    "maxSize": CONFIG['fileMaxSize'],
                    "allowFiles": CONFIG['fileAllowFiles']
                }

            if fieldName in http.request.httprequest.files:
                print(http.request.httprequest.files)
                field = http.request.httprequest.files[fieldName]
                uploader = Uploader(field, config, Config.STATIC_FOLDER)
                result = uploader.getFileInfo()
            else:
                result['state'] = '上传接口出错'

        elif action in ('uploadscrawl',):
            # 涂鸦上传
            fieldName = CONFIG.get('scrawlFieldName')
            config = {
                "pathFormat": CONFIG.get('scrawlPathFormat'),
                "maxSize": CONFIG.get('scrawlMaxSize'),
                "allowFiles": CONFIG.get('scrawlAllowFiles'),
                "oriName": "scrawl.png"
            }
            if fieldName in http.request.httprequest.form:
                field = http.request.httprequest.form[fieldName]
                uploader = Uploader(field, config, Config.STATIC_FOLDER, 'base64')
                result = uploader.getFileInfo()
            else:
                result['state'] = '上传接口出错'

        elif action in ('catchimage',):
            config = {
                "pathFormat": CONFIG['catcherPathFormat'],
                "maxSize": CONFIG['catcherMaxSize'],
                "allowFiles": CONFIG['catcherAllowFiles'],
                "oriName": "remote.png"
            }
            fieldName = CONFIG['catcherFieldName']

            if fieldName in http.request.httprequest.form:
                # 这里比较奇怪，远程抓图提交的表单名称不是这个
                source = []
            elif '%s[]' % fieldName in http.request.httprequest.form:
                # 而是这个
                source = http.request.httprequest.form.getlist('%s[]' % fieldName)

            _list = []
            for imgurl in source:
                uploader = Uploader(imgurl, config, Config.STATIC_FOLDER, 'remote')
                info = uploader.getFileInfo()
                _list.append({
                    'state': info['state'],
                    'url': info['url'],
                    'original': info['original'],
                    'source': imgurl,
                })

            result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
            result['list'] = _list
        else:
            result['state'] = '请求地址出错'

        result = json.dumps(result)

        if 'callback' in http.request.httprequest.args:
            callback = http.request.httprequest.args.get('callback')
            if re.match(r'^[\w_]+$', callback):
                result = '%s(%s)' % (callback, result)
                mimetype = 'application/javascript'
            else:
                result = json.dumps({'state': 'callback参数不合法'})

        # res = make_response(result)
        res = http.request.make_response(result)
        res.mimetype = mimetype
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
        return res

    @http.route('/news/add_cate', methods=['POST'], csrf=False)
    def add_cate(self, **kw):
        req = http.request.httprequest
        if req.method == 'POST':
            categories = http.request.env['news.category'].search([])
            category = req.values.get('new_cate', None)
            if category:
                if category in [cate.name for cate in categories]:
                    message = '类别已存在'
                    data = {
                        'msg': message,
                        'categories': [cate.name for cate in categories]
                    }
                    return json.dumps(data)
                http.request.env['news.category'].create({'name': category})
                data = [{'name': cate.name, 'id': cate.id} for cate in
                        http.request.env['news.category'].search([])]
                print(json.dumps(data))
            return json.dumps(data)

    @http.route('/news/cate/<int:id>', methods=['GET'])
    def get_category(self, id, **kw):
        news_list = http.request.env['news.news']. \
            search([('category', '=', id), ('is_delete', '=', False)]).order_by('-pub_time')
        categories = http.request.env['news.category'].search([])
        news_list, page_data = self._get_pages(news_list, **kw)
        news = self._del_html(news_list)
        data = {
            'news': news,
            'categories': categories
        }
        data.update(page_data)
        return http.request.render('news.index', data)


# class Mysite(Website):
#     @http.route('/', type='http', auth="public", website=True)
#     def index(self):
#         return local_redirect('/news/index')
