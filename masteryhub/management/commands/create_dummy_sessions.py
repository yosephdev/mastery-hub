from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from masteryhub.models import Session, Category
from profiles.models import Profile
from decimal import Decimal
import random
from datetime import timedelta
from django.db import connection

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates dummy sessions for testing'

    def handle(self, *args, **kwargs):
        try:          
            with connection.cursor() as cursor:                
                cursor.execute("""
                    DO $$ 
                    BEGIN 
                        IF EXISTS (
                            SELECT 1 
                            FROM information_schema.table_constraints 
                            WHERE constraint_name='masteryhub_session_host_id_ee00b001_fk_accounts_profile_id'
                        ) THEN
                            ALTER TABLE masteryhub_session 
                            DROP CONSTRAINT masteryhub_session_host_id_ee00b001_fk_accounts_profile_id;
                        END IF;
                    END $$;
                """)                
                
                cursor.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.table_constraints 
                            WHERE constraint_name='masteryhub_session_host_profiles_fk'
                        ) THEN
                            ALTER TABLE masteryhub_session
                            ADD CONSTRAINT masteryhub_session_host_profiles_fk
                            FOREIGN KEY (host_id) REFERENCES profiles_profile(id);
                        END IF;
                    END $$;
                """)
            
            Session.objects.all().delete()
            
            categories = Category.objects.all()
            if not categories:
                self.stdout.write(self.style.ERROR('No categories found'))
                return
            
            expert_profiles = Profile.objects.filter(is_expert=True)
            self.stdout.write(f"Found {expert_profiles.count()} expert profiles")
            
            if not expert_profiles:
                self.stdout.write(self.style.ERROR('No expert profiles found'))
                return
            
            for profile in expert_profiles:
                session = Session.objects.create(
                    title=f"Training Session by {profile.user.username}",
                    description="Learn from an expert in this comprehensive session",
                    duration=timedelta(hours=2),
                    price=Decimal('99.99'),
                    host_id=profile.id,
                    category=random.choice(categories),
                    status="scheduled",
                    max_participants=10,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Created session with host {profile.user.username} (ID: {profile.id})'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))