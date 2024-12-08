from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('masteryhub', '0005_alter_session_host'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE masteryhub_session 
            DROP CONSTRAINT IF EXISTS masteryhub_session_host_id_ee00b001_fk_accounts_profile_id;
            
            ALTER TABLE masteryhub_session
            ADD CONSTRAINT masteryhub_session_host_profiles_fk
            FOREIGN KEY (host_id) REFERENCES profiles_profile(id);
            """,
            reverse_sql="""
            ALTER TABLE masteryhub_session 
            DROP CONSTRAINT IF EXISTS masteryhub_session_host_profiles_fk;
            """
        ),
    ]