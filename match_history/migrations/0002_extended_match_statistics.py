from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        # Add objective statistics to Match model
        migrations.AddField(
            model_name='match',
            name='blue_team_towers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_towers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='blue_team_dragons',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_dragons',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='blue_team_barons',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_barons',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='blue_team_heralds',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_heralds',
            field=models.IntegerField(default=0),
        ),
        
        # Add damage statistics to Participant model
        migrations.AddField(
            model_name='participant',
            name='total_damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='physical_damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='magic_damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='true_damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='total_damage_taken',
            field=models.IntegerField(default=0),
        ),
        
        # Add gold statistics to Participant model
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
        
        # Add vision statistics to Participant model
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
    ]