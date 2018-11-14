# coding:utf8
import math


def paginator(cur_page, offset, total):
    # 总页数<分页: 1-总页数
    # 当前页<分页/2 :1-offset
    # 当前页>（总页数-分页/2）：（总页数-offset+1）-总页数
    # 分页/2 <=当前页<=（总页数-分页/2）:  (当前页-offset/2+1) - (当前页+offset/2)

    middle = int(math.floor(float(offset) / 2))
    if total < offset:
        start = 1
        end = total
    elif cur_page <= middle:
        start = 1
        end = offset
    elif cur_page >= total - middle:
        start = total - offset + 1
        end = total
    else:
        if offset % 2 == 0:
            start = cur_page - middle + 1
        else:
            start = cur_page - middle
        end = cur_page + middle
    return start, end + 1


# if __name__ == '__main__':
#     pages = range(1, 15)
#     for page in pages:
#         s, e = paginator(page, 6, 14)
#         pagelist = range(s, e)
#         index = pagelist.index(page)
#         pagelist[index] = str(page) + '*'
#         print(pagelist)
