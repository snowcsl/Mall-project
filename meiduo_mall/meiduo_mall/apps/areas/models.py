from django.db import models


# Create your models here.
class Area(models.Model):
    """
    行政区
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    # 自关联字段的外键指向自身 ForeignKey('self')
    # related_name指明查询一个行政区划的所有下级行政区划时，使用哪种语法查询   Area模型类对象.subs查询

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
