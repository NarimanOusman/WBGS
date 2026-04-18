from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wau', '0003_alter_project_status_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='projects/'),
        ),
    ]
