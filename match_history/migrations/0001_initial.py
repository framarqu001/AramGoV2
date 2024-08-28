# Generated by Django 4.2.15 on 2024-08-27 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Champion',
            fields=[
                ('champion_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('image_path', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('image_path', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('match_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('game_start', models.DateTimeField()),
                ('game_duration', models.IntegerField()),
                ('game_mode', models.CharField(max_length=50)),
                ('game_version', models.CharField(max_length=50)),
                ('winner', models.IntegerField(choices=[(100, 'Blue Win'), (200, 'Red Win')])),
                ('new_match', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-game_start'],
            },
        ),
        migrations.CreateModel(
            name='ProfileIcon',
            fields=[
                ('profile_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('image_path', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Rune',
            fields=[
                ('rune_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('image_path', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('puuid', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('game_name', models.CharField(blank=True, default='', max_length=50)),
                ('normalized_game_name', models.CharField(blank=True, default='', max_length=50)),
                ('summoner_name', models.CharField(blank=True, default='', max_length=50)),
                ('tag_line', models.CharField(blank=True, default='', max_length=10)),
                ('normalized_tag_line', models.CharField(blank=True, default='', max_length=50)),
                ('summoner_level', models.IntegerField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('task_id', models.CharField(blank=True, max_length=100, null=True)),
                ('being_parsed', models.BooleanField(default=False)),
                ('parsed_matches', models.IntegerField(default=False)),
                ('total_matches', models.IntegerField(default=0)),
                ('profile_icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='match_history.profileicon')),
            ],
        ),
        migrations.CreateModel(
            name='SummonerSpell',
            fields=[
                ('spell_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('image_path', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kills', models.IntegerField()),
                ('deaths', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('creep_score', models.IntegerField()),
                ('team', models.IntegerField(choices=[(100, 'Blue Team'), (200, 'Red Team')])),
                ('win', models.BooleanField()),
                ('game_name', models.CharField(max_length=50)),
                ('champion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='match_history.champion')),
                ('item1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item1', to='match_history.item')),
                ('item2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item2', to='match_history.item')),
                ('item3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item3', to='match_history.item')),
                ('item4', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item4', to='match_history.item')),
                ('item5', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item5', to='match_history.item')),
                ('item6', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants_item6', to='match_history.item')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='match_history.match')),
                ('rune1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='participants_rune1', to='match_history.rune')),
                ('rune2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='participants_rune2', to='match_history.rune')),
                ('spell1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants_spell1', to='match_history.summonerspell')),
                ('spell2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants_spell2', to='match_history.summonerspell')),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='match_history.summoner')),
            ],
        ),
        migrations.CreateModel(
            name='SummonerChampionStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_played', models.IntegerField(default=0)),
                ('duration_played', models.IntegerField(default=0)),
                ('total_creep_score', models.IntegerField(default=0)),
                ('total_wins', models.IntegerField(default=0)),
                ('total_losses', models.IntegerField(default=0)),
                ('total_kills', models.IntegerField(default=0)),
                ('total_deaths', models.IntegerField(default=0)),
                ('total_assists', models.IntegerField(default=0)),
                ('year', models.IntegerField(default=2024)),
                ('champion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summoner_stats', to='match_history.champion')),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='champion_stats', to='match_history.summoner')),
            ],
            options={
                'unique_together': {('summoner', 'champion', 'year')},
            },
        ),
        migrations.CreateModel(
            name='ChampionStatsPatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patch', models.CharField(max_length=10)),
                ('total_played', models.IntegerField(default=0)),
                ('total_wins', models.IntegerField(default=0)),
                ('total_losses', models.IntegerField(default=0)),
                ('champion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='match_history.champion')),
            ],
            options={
                'unique_together': {('champion', 'patch')},
            },
        ),
        migrations.CreateModel(
            name='AccountStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_played', models.IntegerField(default=0)),
                ('total_wins', models.IntegerField(default=0)),
                ('total_losses', models.IntegerField(default=0)),
                ('total_kills', models.IntegerField(default=0)),
                ('total_deaths', models.IntegerField(default=0)),
                ('total_assists', models.IntegerField(default=0)),
                ('snowballs_thrown', models.IntegerField(default=0)),
                ('snowball_hits', models.IntegerField(default=0)),
                ('year', models.IntegerField(default=2024)),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_stats', to='match_history.summoner')),
            ],
            options={
                'unique_together': {('summoner', 'year')},
            },
        ),
    ]
