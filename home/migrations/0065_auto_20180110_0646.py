# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-10 06:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0064_auto_20180110_0630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comrade',
            name='pronouns',
            field=models.CharField(choices=[('she', 'she/her/her'), ('he', 'he/him/him'), ('they', 'they/them/their'), ('fae', 'fae/faer/faer'), ('ey', 'ey/em/eir'), ('per', 'per/per/pers'), ('ve', 've/ver/vis'), ('xe', 'xem/xyr/xyrs'), ('ze', 'hir/hir/hirs')], default=['they', 'them', 'their', 'theirs', 'themself', 'http://pronoun.is/they'], help_text="Your preferred pronoun. This will be used in emails from Outreachy organizers directly to you. The format is subject/object/possessive. Example: '__(subject)__ interned with Outreachy. The mentor liked working with __(object)__. __(possessive)__ project was challenging.", max_length=4, verbose_name='Pronouns'),
        ),
    ]