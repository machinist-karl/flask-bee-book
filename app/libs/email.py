from threading import Thread

from flask import current_app, render_template
from app import mail
from flask_mail import Message

"""
    to: 邮件目标地址
    subject: 邮件标题
    template: html格式的邮件模板
    **kwargs: html页面需要的对象及其对象的属性值，即需要渲染的对象值 
    
    注意: 这里不要使用current_app，因为其是一个代理对象，代理对象会根据其现在的线程号
    去查找数据,send_async_email正好是一个新的线程, 由于线程之间的数据是隔离的,所以新的
    线程在其自身的栈中去查找其它线程的数据是无法找到的
"""


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            raise e


def send_email(to, subject, template, **kwargs):
    msg = Message('[蜜书]' + ' ' + subject,
                  sender=current_app.config['MAIL_USERNAME']
                  , recipients=[to])
    msg.html = render_template(template, **kwargs)
    # 该方法需要不是代理类直接提供的功能
    # 代理类会根据场景的不同,在内部对该函数进行不同的实现
    # 最后通过object.__setattr__()将该函数名称加入到对象的属性中
    app = current_app._get_current_object()
    t = Thread(target=send_async_email, args=[app, msg])
    t.start()
