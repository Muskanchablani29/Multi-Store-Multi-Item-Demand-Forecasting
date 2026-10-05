from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='sale', name='unit_price',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='cost_price',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='discount_percent',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='discount_amount',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='total_sales',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='profit',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='promotion',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='sale', name='promotion_type',
            field=models.CharField(blank=True, default='No Promotion', max_length=50)),
        migrations.AddField(model_name='sale', name='promotion_discount',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='sale', name='is_holiday',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='sale', name='holiday_name',
            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='sale', name='season',
            field=models.CharField(blank=True, default='', max_length=50)),
        migrations.AddField(model_name='sale', name='day_of_week',
            field=models.IntegerField(default=0)),
        migrations.AddField(model_name='sale', name='is_weekend',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='sale', name='month',
            field=models.IntegerField(default=1)),
        migrations.AddField(model_name='sale', name='week_number',
            field=models.IntegerField(default=1)),
    ]
