from django.db import migrations


def fix_profile_references(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    cursor.execute("""
    ALTER TABLE masteryhub_session_participants 
    DROP CONSTRAINT IF EXISTS masteryhub_session_p_profile_id_d9af3035_fk_accounts_;
    
    ALTER TABLE masteryhub_session_participants
    ADD CONSTRAINT masteryhub_session_participants_profile_fk
    FOREIGN KEY (profile_id) REFERENCES profiles_profile(id)
    ON DELETE CASCADE;
    """)


class Migration(migrations.Migration):
    dependencies = [
        ('masteryhub', '0014_alter_session_participants'),
        ('profiles', '0003_alter_profile_github_profile'),
    ]

    operations = [
        migrations.RunPython(fix_profile_references),
    ]
