# Generated migration for participant rank fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='tier',
            field=models.CharField(
                choices=[
                    ('IRON', 'Iron'),
                    ('BRONZE', 'Bronze'),
                    ('SILVER', 'Silver'),
                    ('GOLD', 'Gold'),
                    ('PLATINUM', 'Platinum'),
                    ('EMERALD', 'Emerald'),
                    ('DIAMOND', 'Diamond'),
                    ('MASTER', 'Master'),
                    ('GRANDMASTER', 'Grandmaster'),
                    ('CHALLENGER', 'Challenger'),
                    ('UNRANKED', 'Unranked'),
                ],
                db_index=True,
                default='UNRANKED',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='participant',
            name='division',
            field=models.CharField(
                blank=True,
                choices=[
                    ('I', 'I'),
                    ('II', 'II'),
                    ('III', 'III'),
                    ('IV', 'IV'),
                    ('', 'N/A'),
                ],
                db_index=True,
                default='',
                max_length=5
            ),
        ),
        migrations.AddField(
            model_name='participant',
            name='lp',
            field=models.IntegerField(
                db_index=True,
                default=0,
                help_text='League Points'
            ),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['tier', 'division'], name='match_history_participant_tier_division_idx'),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['summoner', 'tier'], name='match_history_participant_summoner_tier_idx'),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['match', 'tier'], name='match_history_participant_match_tier_idx'),
        ),
    ]