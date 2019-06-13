# coding=utf-8


# 解决py2.7中文出现write错误的问题
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# 解决py2.7中文出现write错误的问题 #

import os

import urllib2
import hashlib
import re

from pyquery import PyQuery as pq

temp_url = "https://mp.weixin.qq.com/s?__biz=MzIxNDEzNzI4Mg==&mid=2653344721&idx=2&sn=6821a114166f5d816bc9fbd5c56d57aa&chksm=8c7e537cbb09da6ac6546de8c83342c712de5f5754d33b614676f44cb61d01346f527577c0ca&mpshare=1&scene=1&srcid=&key=c8c9cb9453e09350da538cf3f7a75f35e4e9f64f652873264a44ba9663b7e484ae3008ea8722ab5e4c42c5817bf275920bf3df3e4e3e640b3c318d20cb130152f7069d2ce1ae01e61e95cef377cf254e&ascene=0&uin=MTcyNDI4ODE1&devicetype=iMac+MacBookPro9%2C2+OSX+OSX+10.14.3+build(18D109)&version=12020810&nettype=WIFI&lang=zh_CN&fontScale=100&pass_ticket=YD2p8V2JqPM7ouW1CnBoby%2BcXrBhIW9nRScMpAFpugM%3D"
file_name = "test.html"

def get_md5(s):
    m2 = hashlib.md5()
    m2.update(s)
    return m2.hexdigest()


def down_file_from_response(response, file_path):
    buff_size = 8192
    with open(file_path, "wb") as download_file:
        while True:
            buff = response.read(buff_size)
            if not buff:
                break
            download_file.write(buff)

doc = pq(temp_url)

title = doc(".rich_media_title").text().strip()
# 设置文章标题
doc("title").text(title)

# 移除head部分标签
for link_item in doc("link").items():
    if link_item.attr("rel").find("shortcut") > -1:
        link_item.remove()
    if link_item.attr("rel").find("mask-icon") > -1:
        link_item.remove()
    if link_item.attr("rel").find("apple-touch-icon-precomposed") > -1:
        link_item.remove()

# 移除PC板式的二维码
doc(".qr_code_pc").remove()

# 移除头尾不需要的部分
doc(".rich_media_title").remove()
doc(".rich_media_meta_list").remove()
doc(".article_modify_area").remove()
doc(".rich_media_tool").remove()
doc("script").remove()
doc("body").append('''
<script type="text/javascript" charset="utf-8" src="./js/jquery.min.js"></script>

<script type="text/javascript">
    $(document).ready(function(){
        $("img").each(function(){
            var dataSrc = $(this).attr("data-src");
            if((typeof(dataSrc) === "string") && dataSrc.length > 0){
                $(this).attr("src", dataSrc);
            }
        })
    });
</script>
''')
all_html = doc.outer_html(method='html')

# 提取所有http/https 的url
search_wx_http_img_reg = re.compile(r'(https{0,1}[:]\/\/.*?)["\')]')
for src in search_wx_http_img_reg.findall(all_html):
    new_file_name = get_md5(src) + ".jpg"
    save_path = os.path.join("img", new_file_name)
    res = urllib2.urlopen(urllib2.Request(url=src, headers={"Referer": "https://mp.weixin.qq.com/s"}))
    down_file_from_response(res, save_path)
    print new_file_name
    all_html = all_html.replace(src, "./img/"+new_file_name)

with open(file_name, "w") as page_file:
    page_file.write(all_html)
