# Generated by Django 5.0.14 on 2025-07-24 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sample_app', '0002_question_question_type_alter_answer_content_choice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/', verbose_name='関連画像'),
        ),
    ]
