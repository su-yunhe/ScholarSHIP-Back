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
