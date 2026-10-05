from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='inventory', name='safety_stock',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='inventory', name='lead_time_days',
            field=models.IntegerField(default=7)),
    ]
