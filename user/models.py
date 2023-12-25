from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    # image = models.ImageField(max_length=128)
    scholar_id = models.CharField(max_length=128, default="")
    organization = models.CharField(max_length=128, default="")
    introduction = models.TextField(max_length=128, default="")
    real_name = models.CharField(max_length=128, default="")
    user_degree = models.CharField(max_length=128, default="")

    def __str__(self):
        return self.userName

    class Meta:
        db_table = "users"


class Concern(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default="0")
    scholar_id = models.CharField(max_length=128, default="")
    isDelete = models.BooleanField(default=False)
    name = models.CharField(max_length=128, default="")

    class Meta:
        db_table = "user_concern"


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default="0")
    name = models.CharField(max_length=128, default="")
    isDelete = models.BooleanField(default=False)

    class Meta:
        db_table = "user_label"


class Star(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default="0")
    label_id = models.IntegerField(default="0")
    article_id = models.TextField(default="")
    time = models.CharField(max_length=128, default="")
    isDelete = models.BooleanField(default=False)
    title = models.TextField(default="")
    content = models.TextField(default="")
    cite_count = models.CharField(max_length=128, default="")
    # author_name=models.CharField(max_length=128, default="")
    # author_id=models.TextField(default="")

    class Meta:
        db_table = "user_star"


class History(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default="0")
    type = models.IntegerField(default="0")
    real_id = models.TextField(default="")
    time = models.DateTimeField(default="")
    isDelete = models.BooleanField(default=False)
    name = models.TextField(default="")

    class Meta:
        db_table = "user_browse_history"


class ArticleAuthor(models.Model):
    id = models.AutoField(primary_key=True)
    article_id = models.CharField(max_length=128, default="")
    scholar_name = models.CharField(max_length=128, default="")

    class Meta:
        db_table = "article_author"
