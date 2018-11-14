# coding:utf8
import os


class Config():
    # 静态文件路径
    STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')