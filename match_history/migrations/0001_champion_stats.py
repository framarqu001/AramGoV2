from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('match_history', '0001_initial'),  # Adjust this to match your actual initial migration
    ]

    operations = [
        migrations.AddField(
            model_name='championstatspatch',
            name='pick_rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='championstatspatch',
            name='average_kda',
            field=models.FloatField(default=0.0),
        ),
        migrations.CreateModel(
            name='ChampionStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patch', models.CharField(max_length=10)),
                ('games_played', models.IntegerField(default=0)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('pick_rate', models.FloatField(default=0.0)),
                ('champion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='champion_stats', to='match_history.Champion')),
            ],
            options={
                'unique_together': {('champion', 'patch')},
            },
        ),
    ]