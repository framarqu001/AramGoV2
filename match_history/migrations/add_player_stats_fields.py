from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),  # Replace with the name of your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='vision_score',
            field=models.IntegerField(default=0),
        ),
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
    ]