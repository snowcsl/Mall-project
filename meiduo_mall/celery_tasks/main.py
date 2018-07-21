# celery的启动文件

from celery import Celery

# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建celery应用
app = Celery('meiduo')  # 所有的属性和所有的方法都在app这个对象下面,通过app这个对象对相应的对象和方法进行调用
                        # meiduo 根据项目名  随意命名的
# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])
