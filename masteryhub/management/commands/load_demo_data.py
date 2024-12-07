from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from profiles.models import Profile
from masteryhub.models import Mentor, Skill, Category
from decimal import Decimal

# Add the skills from create_dummy_mentors
ADDITIONAL_SKILLS = [
    ("AWS Cloud Services", "web_dev"),
    ("Azure Cloud Computing", "web_dev"),
    ("Blockchain Development", "programming"),
    ("Computer Vision", "data_science"),
    ("Cybersecurity Fundamentals", "programming"),
    ("Digital Marketing", "web_dev"),
    ("Ethical Hacking", "programming"),
    ("Graphic Design", "web_dev"),
    ("IoT Development", "programming"),
    ("Podcast Production", "web_dev"),
    ("Video Production", "web_dev")
]


class Command(BaseCommand):
    help = 'Loads demo data for mentors without deleting existing data'

    def handle(self, *args, **kwargs):
        """
        Handle method that accepts **kwargs to properly handle command arguments like verbosity
        """
        try:
            # Create categories
            categories = {}

            # Programming category
            programming_cat, _ = Category.objects.get_or_create(
                name='Programming',
                defaults={'description': 'Programming and Development'}
            )
            categories['programming'] = programming_cat

            # Web Development category
            web_dev_cat, _ = Category.objects.get_or_create(
                name='Web Development',
                defaults={'description': 'Web Development Skills'}
            )
            categories['web_dev'] = web_dev_cat

            # Data Science category
            data_science_cat, _ = Category.objects.get_or_create(
                name='Data Science',
                defaults={'description': 'Data Science and Analytics'}
            )
            categories['data_science'] = data_science_cat

            # Debug: Print categories
            self.stdout.write(self.style.SUCCESS('Created categories:'))
            for key, category in categories.items():
                self.stdout.write(f"- {key}: {category.id} - {category.name}")

            # Define skills with their categories
            skills_data = [
                {
                    'title': 'Python',
                    'category_key': 'programming',
                    'description': 'Expertise in Python programming language'
                },
                {
                    'title': 'Django',
                    'category_key': 'web_dev',
                    'description': 'Web development with Django framework'
                },
                {
                    'title': 'JavaScript',
                    'category_key': 'web_dev',
                    'description': 'Frontend and backend JavaScript development'
                },
                {
                    'title': 'React',
                    'category_key': 'web_dev',
                    'description': 'Frontend development with React'
                },
                {
                    'title': 'Machine Learning',
                    'category_key': 'data_science',
                    'description': 'Machine Learning and AI development'
                },
                {
                    'title': 'Data Analysis',
                    'category_key': 'data_science',
                    'description': 'Data analysis and visualization'
                },
                {
                    'title': 'SQL',
                    'category_key': 'data_science',
                    'description': 'Database management and SQL queries'
                },
            ]

            # Add additional skills to skills_data
            for skill_name, category_key in ADDITIONAL_SKILLS:
                skills_data.append({
                    'title': skill_name,
                    'category_key': category_key,
                    'description': f'Expertise in {skill_name}'
                })

            # Create skills
            skills_map = {}
            for skill_data in skills_data:
                category = categories[skill_data['category_key']]

                try:
                    Skill.objects.filter(title=skill_data['title']).delete()

                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO masteryhub_skill 
                            (title, name, description, category, category_id, created_at, price) 
                            VALUES 
                            (%s, %s, %s, %s, %s, NOW(), NULL)
                            RETURNING id;
                        """, [
                            skill_data['title'],
                            skill_data['title'].lower().replace(' ', '_'),
                            skill_data['description'],
                            category.name,
                            category.id,
                        ])

                        skill_id = cursor.fetchone()[0]

                        cursor.execute("""
                            SELECT title, category, category_id FROM masteryhub_skill WHERE id = %s
                        """, [skill_id])
                        result = cursor.fetchone()
                        self.stdout.write(
                            f"Verified insertion - Title: {result[0]}, Category: {result[1]}, Category ID: {result[2]}")

                    skill = Skill.objects.get(id=skill_id)
                    skills_map[skill_data['title']] = skill

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created skill: {skill_data['title']} in category {category.name}")
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error creating skill {skill_data['title']}: {str(e)}")
                    )
                    self.stdout.write(f"Category ID: {category.id}")
                    self.stdout.write(f"Category Name: {category.name}")
                    self.stdout.write(f"Full skill data: {skill_data}")
                    raise

            demo_mentors = [
                {
                    'username': 'sarah_tech',
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'email': 'sarah@example.com',
                    'profile': {
                        'bio': 'Senior Software Engineer with 8 years of experience.',
                        'is_expert': True,
                        'expertise_areas': 'Python, Django, JavaScript',
                        'years_of_experience': 8,
                        'hourly_rate': 75.00,
                        'availability': 'Evenings and weekends'
                    },
                    'mentor': {
                        'experience_level': 'expert',
                        'rating': 4.9,
                        'is_available': True,
                        'hourly_rate': Decimal('75.00'),
                        'skills': ['Python', 'Django', 'JavaScript']
                    }
                },
                {
                    'username': 'david_data',
                    'first_name': 'David',
                    'last_name': 'Chen',
                    'email': 'david@example.com',
                    'profile': {
                        'bio': 'Data Scientist specializing in Machine Learning and Analytics.',
                        'is_expert': True,
                        'expertise_areas': 'Machine Learning, Data Analysis, Python',
                        'years_of_experience': 6,
                        'hourly_rate': 85.00,
                        'availability': 'Weekday afternoons'
                    },
                    'mentor': {
                        'experience_level': 'expert',
                        'rating': 4.8,
                        'is_available': True,
                        'hourly_rate': Decimal('85.00'),
                        'skills': ['Python', 'Machine Learning', 'Data Analysis']
                    }
                },
                {
                    'username': 'maria_web',
                    'first_name': 'Maria',
                    'last_name': 'Garcia',
                    'email': 'maria@example.com',
                    'profile': {
                        'bio': 'Frontend Developer passionate about creating beautiful user experiences.',
                        'is_expert': True,
                        'expertise_areas': 'React, JavaScript, Web Development',
                        'years_of_experience': 5,
                        'hourly_rate': 65.00,
                        'availability': 'Flexible schedule'
                    },
                    'mentor': {
                        'experience_level': 'intermediate',
                        'rating': 4.7,
                        'is_available': True,
                        'hourly_rate': Decimal('65.00'),
                        'skills': ['JavaScript', 'React']
                    }
                },
                {
                    'username': 'alex_data',
                    'first_name': 'Alex',
                    'last_name': 'Thompson',
                    'email': 'alex@example.com',
                    'profile': {
                        'bio': 'Database expert with strong focus on data analytics and SQL optimization.',
                        'is_expert': True,
                        'expertise_areas': 'SQL, Data Analysis, Python',
                        'years_of_experience': 7,
                        'hourly_rate': 70.00,
                        'availability': 'Morning sessions'
                    },
                    'mentor': {
                        'experience_level': 'expert',
                        'rating': 4.9,
                        'is_available': True,
                        'hourly_rate': Decimal('70.00'),
                        'skills': ['SQL', 'Data Analysis', 'Python']
                    }
                },
                {
                    'username': 'james_full',
                    'first_name': 'James',
                    'last_name': 'Wilson',
                    'email': 'james@example.com',
                    'profile': {
                        'bio': 'Full-stack developer specialized in Django and React applications.',
                        'is_expert': True,
                        'expertise_areas': 'Django, React, JavaScript, Python',
                        'years_of_experience': 4,
                        'hourly_rate': 60.00,
                        'availability': 'Weekends only'
                    },
                    'mentor': {
                        'experience_level': 'intermediate',
                        'rating': 4.6,
                        'is_available': True,
                        'hourly_rate': Decimal('60.00'),
                        'skills': ['Python', 'Django', 'React', 'JavaScript']
                    }
                }
            ]

            # Create mentors
            for mentor_data in demo_mentors:
                try:
                    username = mentor_data['username']
                    profile_data = mentor_data.pop('profile')
                    mentor_info = mentor_data.pop('mentor')

                    # Get or create user
                    user, user_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': mentor_data['email'],
                            'first_name': mentor_data['first_name'],
                            'last_name': mentor_data['last_name'],
                            'is_active': True
                        }
                    )

                    # Update user fields if user exists
                    if not user_created:
                        user.email = mentor_data['email']
                        user.first_name = mentor_data['first_name']
                        user.last_name = mentor_data['last_name']
                        user.save()

                    # Get or create profile
                    profile, profile_created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'bio': profile_data['bio'],
                            'is_expert': profile_data['is_expert'],
                            'availability': profile_data['availability'],
                            'skills': profile_data.get('expertise_areas', ''),
                            'is_available': True,
                            'mentorship_areas': profile_data.get('expertise_areas', ''),
                            'preferred_mentoring_method': 'One-on-one'
                        }
                    )

                    # Update profile if it exists
                    if not profile_created:
                        profile.bio = profile_data['bio']
                        profile.is_expert = profile_data['is_expert']
                        profile.availability = profile_data['availability']
                        profile.skills = profile_data.get(
                            'expertise_areas', '')
                        profile.is_available = True
                        profile.mentorship_areas = profile_data.get(
                            'expertise_areas', '')
                        profile.preferred_mentoring_method = 'One-on-one'
                        profile.save()

                    # Get or create mentor
                    mentor, mentor_created = Mentor.objects.get_or_create(
                        user=user,
                        defaults={
                            'bio': profile_data['bio'],
                            'rating': mentor_info['rating'],
                            'is_available': mentor_info['is_available'],
                            'experience_level': mentor_info['experience_level'],
                            'hourly_rate': mentor_info['hourly_rate']
                        }
                    )

                    # Update mentor if it exists
                    if not mentor_created:
                        mentor.bio = profile_data['bio']
                        mentor.rating = mentor_info['rating']
                        mentor.is_available = mentor_info['is_available']
                        mentor.experience_level = mentor_info['experience_level']
                        mentor.hourly_rate = mentor_info['hourly_rate']
                        mentor.save()

                    # Update mentor skills
                    mentor_skills = [skills_map[skill_name]
                                     for skill_name in mentor_info['skills']]
                    mentor.skills.set(mentor_skills)

                    action = "Created" if all(
                        [user_created, profile_created, mentor_created]) else "Updated"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{action} mentor: {user.get_full_name()}")
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error processing mentor {mentor_data.get('username', 'unknown')}: {str(e)}")
                    )
                    import traceback
                    self.stdout.write(self.style.ERROR(traceback.format_exc()))
                    raise

            self.stdout.write(self.style.SUCCESS(
                'Successfully loaded all demo data'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading demo data: {str(e)}')
            )
