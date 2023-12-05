# Generated by Django 3.2 on 2023-11-29 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concern',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default='0')),
                ('scholar_id', models.CharField(default='', max_length=128)),
                ('isDelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_concern',
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default='0')),
                ('type', models.IntegerField(default='0')),
                ('real_id', models.TextField(default='')),
                ('time', models.DateTimeField(default='')),
                ('isDelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_browse_history',
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default='0')),
                ('name', models.CharField(default='', max_length=128)),
                ('isDelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_label',
            },
        ),
        migrations.CreateModel(
            name='Star',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default='0')),
                ('label_id', models.IntegerField(default='0')),
                ('article_id', models.TextField(default='')),
                ('time', models.DateTimeField(default='')),
                ('isDelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_star',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=128, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('scholar_id', models.CharField(default='', max_length=128)),
                ('organization', models.CharField(default='', max_length=128)),
                ('introduction', models.TextField(default='', max_length=128)),
                ('real_name', models.CharField(default='', max_length=128)),
                ('user_degree', models.CharField(default='', max_length=128)),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]