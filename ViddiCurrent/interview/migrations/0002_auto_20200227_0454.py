# Generated by Django 3.0.2 on 2020-02-27 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='about',
            field=models.TextField(blank=True, verbose_name='About'),
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.TextField(blank=True, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='img',
            field=models.ImageField(default=22, upload_to=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='end_date',
            field=models.DateField(default='27/02/2020'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='start_date',
            field=models.DateField(default='27/02/2020'),
        ),
    ]
