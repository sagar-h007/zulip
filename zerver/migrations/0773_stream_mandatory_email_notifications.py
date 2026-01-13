from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0772_clean_up_imageattachments"),
    ]

    operations = [
        migrations.AddField(
            model_name="stream",
            name="mandatory_email_notifications",
            field=models.BooleanField(default=False),
        ),
    ]
