# Generated migration for adding rank fields to Summoner model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # This migration adds rank fields to existing Summoner model
    ]

    operations = [
        migrations.AddField(
            model_name='summoner',
            name='tier',
            field=models.CharField(blank=True, choices=[('IRON', 'Iron'), ('BRONZE', 'Bronze'), ('SILVER', 'Silver'), ('GOLD', 'Gold'), ('PLATINUM', 'Platinum'), ('EMERALD', 'Emerald'), ('DIAMOND', 'Diamond'), ('MASTER', 'Master'), ('GRANDMASTER', 'Grandmaster'), ('CHALLENGER', 'Challenger')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='division',
            field=models.CharField(blank=True, choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV')], max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='league_points',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]