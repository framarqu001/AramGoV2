# Generated migration for enhanced match statistics

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),  # Adjust this based on your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='total_damage_dealt_to_champions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='total_damage_taken',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='magic_damage_dealt_to_champions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='physical_damage_dealt_to_champions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='true_damage_dealt_to_champions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_self_mitigated',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='vision_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='wards_placed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='wards_killed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='vision_wards_bought_in_game',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='turret_kills',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='inhibitor_kills',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='dragon_kills',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='baron_kills',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='gold_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='gold_spent',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='total_heal',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='total_units_healed',
            field=models.IntegerField(default=0),
        ),
    ]