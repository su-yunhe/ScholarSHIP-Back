# Generated by Django 3.2 on 2023-12-26 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20231225_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(default='', max_length=128),
        ),
    ]