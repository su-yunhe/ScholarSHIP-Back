import json

from django.db.models import *


class Ban(Model):
    work_id = CharField(primary_key=True, max_length=100)
    author_id = JSONField()
