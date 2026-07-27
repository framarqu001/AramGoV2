from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='champion',
            name='primary_role',
            field=models.CharField(choices=[('tank', 'Tank'), ('fighter', 'Fighter'), ('mage', 'Mage'), ('assassin', 'Assassin'), ('marksman', 'Marksman'), ('support', 'Support')], default='fighter', max_length=20),
        ),
        migrations.AddField(
            model_name='champion',
            name='secondary_role',
            field=models.CharField(blank=True, choices=[('tank', 'Tank'), ('fighter', 'Fighter'), ('mage', 'Mage'), ('assassin', 'Assassin'), ('marksman', 'Marksman'), ('support', 'Support')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='champion',
            name='damage_type',
            field=models.CharField(choices=[('physical', 'Physical'), ('magical', 'Magical'), ('mixed', 'Mixed')], default='physical', max_length=20),
        ),
        migrations.CreateModel(
            name='TeamComposition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.IntegerField(choices=[(100, 'Blue Team'), (200, 'Red Team')])),
                ('role_distribution', models.JSONField(default=dict)),
                ('damage_distribution', models.JSONField(default=dict)),
                ('synergy_score', models.IntegerField(default=0)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_compositions', to='match_history.match')),
            ],
            options={
                'unique_together': {('match', 'team')},
            },
        ),
    ]