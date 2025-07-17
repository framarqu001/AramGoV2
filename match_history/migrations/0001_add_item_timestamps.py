from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='item1_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='item2_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='item3_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='item4_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='item5_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='item6_timestamp',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]