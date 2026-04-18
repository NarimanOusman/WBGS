from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wau', '0002_projectimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(
                choices=[('Planned', 'Planned'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')],
                default='Planned',
                max_length=20,
            ),
        ),
    ]
