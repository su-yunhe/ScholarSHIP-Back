from django.db import models


# Create your models here.
class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    # image = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.userName

    class Meta:
        db_table = "manager"


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default="0")
    scholar_id = models.CharField(max_length=128, default="")
    email = models.EmailField(unique=True)
    content = models.TextField(default="")
    time = models.DateTimeField(default="")
    status = models.CharField(max_length=128, default="0")
    user_name = models.CharField(max_length=128, default="")
    scholar_name = models.CharField(max_length=128, default="")
    ins_name = models.TextField(default="")

    class Meta:
        db_table = "scholar_apply"
