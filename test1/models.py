from django.db import models
class Test(models.Model):
    id=models.AutoField(primary_key=True)
    include=models.TextField(default="")
    class Meta:
        db_table = "test"
# Create your models here.
