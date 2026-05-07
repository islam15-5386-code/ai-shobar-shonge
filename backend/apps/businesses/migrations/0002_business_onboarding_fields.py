from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='business',
            name='business_hours',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='business',
            name='category',
            field=models.CharField(blank=True, default='shop', max_length=50),
        ),
        migrations.AddField(
            model_name='business',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='business_logos/'),
        ),
        migrations.AddField(
            model_name='business',
            name='logo_extracted_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='business',
            name='support_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='business',
            name='support_phone',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
