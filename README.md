# # Python Web项目
1、基于Flask的轻量级的图书交换网站

2、前端: HTML + CSS + JS + 模板渲染方式（Jinja2）

3、后端: Flask + Flask插件 +  Mysql

4、实现简单的注册登录

5、图书的查找采用第三方API的调用

6、图书交换采用简单的订单的方式

7、学习时注意先要找到一种可用的第三方图书查询API，本项目不提供第三方的API Key供调用；若使用第三方API，可能需要对model进行改造以适配前端数据展示，改造涉及如下几个文件：

1）app --> secure.py --> secure.py

2）app --> spider --> bee_book.py

3）app --> view_models --> book.py
