from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='gold_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='vision_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_taken',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='healing_done',
            field=models.IntegerField(default=0),
        ),
    ]