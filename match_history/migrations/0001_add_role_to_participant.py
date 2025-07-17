from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='role',
            field=models.CharField(blank=True, choices=[('TANK', 'Tank'), ('BRUISER', 'Bruiser'), ('MAGE', 'Mage'), ('MARKSMAN', 'Marksman'), ('SUPPORT', 'Support'), ('ASSASSIN', 'Assassin')], max_length=20, null=True),
        ),
    ]