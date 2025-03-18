from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import Profile
from masteryhub.models import Mentor, Skill, Category
from decimal import Decimal
import random
from datetime import date

MENTOR_DATA = {
    'david': {
        'full_name': 'David Johnson',
        'bio': 'Full Stack Developer with expertise in Java and Python. I have worked with major corporations to develop scalable applications.',
        'skills': ['Java Programming', 'Python Programming', 'React'],
        'experience_level': 'advanced',
        'hourly_rate': 85.00,
        'availability': 'Weekday evenings and weekends',
        'mentorship_areas': 'Software Architecture, Backend Development, Full Stack Development',
        'is_available': True,
        'rating': 4.8
    },
    'maria_web': {
        'full_name': 'Maria Garcia',
        'bio': 'Frontend specialist with 6+ years experience creating responsive and user-friendly interfaces.',
        'skills': ['JavaScript', 'React', 'HTML/CSS', 'UI/UX Design'],
        'experience_level': 'advanced',
        'hourly_rate': 75.00,
        'availability': 'Flexible hours, prefer mornings',
        'mentorship_areas': 'Frontend Development, UI/UX Design, Web Accessibility',
        'is_available': True,
        'rating': 4.7
    },
    'yoseph': {
        'full_name': 'Yoseph Berhane Gebremedhin',
        'bio': 'Full Stack Developer with focus on Django and React. Expert in building e-commerce applications and payment systems.',
        'skills': ['Python Programming', 'Django', 'React', 'Payment Systems'],
        'experience_level': 'expert',
        'hourly_rate': 90.00,
        'availability': 'Weekdays 10am-6pm',
        'mentorship_areas': 'Full Stack Development, E-commerce Solutions, Stripe Integration',
        'is_available': True,
        'rating': 4.9
    },
    'sarah_tech': {
        'full_name': 'Sarah Johnson',
        'bio': 'Tech lead with expertise in cloud architecture and DevOps practices.',
        'skills': ['AWS Cloud Services', 'Docker', 'Kubernetes', 'CI/CD'],
        'experience_level': 'expert',
        'hourly_rate': 95.00,
        'availability': 'Weekends and Thursday evenings',
        'mentorship_areas': 'Cloud Architecture, DevOps, CI/CD Implementation',
        'is_available': True,
        'rating': 4.8
    },
    'david_data': {
        'full_name': 'David Chen',
        'bio': 'Data scientist specializing in machine learning and predictive analytics with 8+ years of industry experience.',
        'skills': ['Machine Learning', 'Data Analysis', 'Python Programming', 'SQL'],
        'experience_level': 'expert',
        'hourly_rate': 100.00,
        'availability': 'Tuesday and Thursday afternoons',
        'mentorship_areas': 'Machine Learning, Data Science, Predictive Analytics',
        'is_available': True,
        'rating': 4.9
    },
    'sarah': {
        'full_name': 'Sarah Smith',
        'bio': 'UI/UX Designer focused on creating accessible and intuitive user experiences.',
        'skills': ['UI/UX Design', 'Adobe XD', 'Figma', 'User Research'],
        'experience_level': 'intermediate',
        'hourly_rate': 70.00,
        'availability': 'Mondays and Wednesdays',
        'mentorship_areas': 'UI/UX Design, Accessibility, User Research',
        'is_available': True,
        'rating': 4.6
    },
    'maria': {
        'full_name': 'Maria Garcia',
        'bio': 'Marketing specialist with expertise in SEO and content strategy.',
        'skills': ['Digital Marketing', 'SEO', 'Content Strategy', 'Social Media'],
        'experience_level': 'advanced',
        'hourly_rate': 80.00,
        'availability': 'Weekday mornings',
        'mentorship_areas': 'Digital Marketing, SEO Optimization, Content Creation',
        'is_available': True,
        'rating': 4.7
    },
    'admin': {
        'full_name': 'Admin User',
        'bio': 'System administrator and security expert with 10+ years of experience in maintaining and securing web applications.',
        'skills': ['Cybersecurity Fundamentals', 'Network Administration', 'Linux Systems'],
        'experience_level': 'expert',
        'hourly_rate': 110.00,
        'availability': 'By appointment only',
        'mentorship_areas': 'System Administration, Security Best Practices, Network Security',
        'is_available': True,
        'rating': 4.9
    },
    'Kidist': {
        'full_name': 'Kidist Shibre',
        'bio': 'Educational Psychologist with PhD in Educational Psychology, specializing in learning strategies and educational technology.',
        'skills': ['Educational Psychology', 'Learning Strategies', 'Educational Technology'],
        'experience_level': 'expert',
        'hourly_rate': 90.00,
        'availability': 'Weekdays 9am-5pm',
        'mentorship_areas': 'Educational Psychology, Learning Strategies, Educational Technology',
        'specialty': 'Educational Psychologist',
        'is_available': True,
        'rating': 4.9
    },
    'Sara': {
        'full_name': 'Sara Taye',
        'bio': 'Business strategist with MBA and 8+ years experience in business development and growth strategies.',
        'skills': ['Business Strategy', 'Market Analysis', 'Business Development'],
        'experience_level': 'advanced',
        'hourly_rate': 85.00,
        'availability': 'Tuesday through Thursday',
        'mentorship_areas': 'Business Strategy, Market Analysis, Growth Planning',
        'specialty': 'Business Strategy',
        'is_available': True,
        'rating': 4.8
    },
    'Alex': {
        'full_name': 'Alex Jacob',
        'bio': 'Senior software engineer with 10+ years experience in full-stack development, specializing in scalable applications.',
        'skills': ['Full Stack Development', 'JavaScript', 'Python Programming', 'System Architecture'],
        'experience_level': 'expert',
        'hourly_rate': 95.00,
        'availability': 'Weekends and evenings',
        'mentorship_areas': 'Software Architecture, Full Stack Development, Career Development',
        'specialty': 'Software Development',
        'is_available': True,
        'rating': 4.7
    },
    'Anna': {
        'full_name': 'Anna Carolina',
        'bio': 'Nutrition expert and health coach with 12+ years experience in health and wellness coaching.',
        'skills': ['Nutrition', 'Health Coaching', 'Wellness Programs'],
        'experience_level': 'expert',
        'hourly_rate': 80.00,
        'availability': 'Monday, Wednesday, Friday',
        'mentorship_areas': 'Nutrition Planning, Health Coaching, Wellness Programs',
        'specialty': 'Nutrition Expert',
        'is_available': True,
        'rating': 4.9
    }
}

class Command(BaseCommand):
    help = 'Updates existing mentor profiles with more detailed information'

    def handle(self, *args, **kwargs):
        try:
            # Create skill categories if needed
            categories = {}
            category_data = [
                ('Programming', 'Learn programming languages and software development'),
                ('Web Development', 'Frontend and backend web development skills'),
                ('Data Science', 'Data analysis, visualization, and machine learning'),
                ('Design', 'UI/UX and graphic design'),
                ('Business', 'Business strategy and entrepreneurship'),
                ('Marketing', 'Digital marketing and growth strategies'),
                ('Education', 'Teaching and learning methodologies'),
                ('Health', 'Health and wellness coaching'),
            ]
            
            for name, description in category_data:
                category, created = Category.objects.get_or_create(
                    name=name, 
                    defaults={'description': description}
                )
                categories[name.lower()] = category
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

            # Ensure all needed skills exist
            all_skills = set()
            for data in MENTOR_DATA.values():
                all_skills.update(data['skills'])
            
            skill_mapping = {}
            for skill_name in all_skills:
                # Determine category based on skill name
                category = self._get_category_for_skill(skill_name, categories)
                
                skill, created = Skill.objects.get_or_create(
                    title=skill_name,
                    defaults={
                        'name': skill_name.lower().replace(' ', '_').replace('/', '_'),
                        'category': category,
                        'description': f'Expertise in {skill_name}'
                    }
                )
                
                skill_mapping[skill_name] = skill
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created skill: {skill_name}'))
            
            # Update mentor profiles
            for username, data in MENTOR_DATA.items():
                try:
                    # Get user
                    user = User.objects.get(username=username)
                    
                    # Update profile
                    profile, created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'bio': data['bio'],
                            'is_expert': True,
                            'skills': ', '.join(data['skills']),
                            'mentorship_areas': data['mentorship_areas'],
                            'availability': data['availability']
                        }
                    )
                    
                    if not created:
                        profile.bio = data['bio']
                        profile.is_expert = True
                        profile.skills = ', '.join(data['skills'])
                        profile.mentorship_areas = data['mentorship_areas']
                        profile.availability = data['availability']
                        profile.save()
                    
                    # Create or update mentor record
                    mentor, mentor_created = Mentor.objects.get_or_create(
                        user=user,
                        defaults={
                            'bio': data['bio'],
                            'experience_level': data['experience_level'],
                            'hourly_rate': Decimal(str(data['hourly_rate'])),
                            'is_available': data['is_available'],
                            'rating': data['rating']
                        }
                    )
                    
                    if not mentor_created:
                        mentor.bio = data['bio']
                        mentor.experience_level = data['experience_level']
                        mentor.hourly_rate = Decimal(str(data['hourly_rate']))
                        mentor.is_available = data['is_available']
                        mentor.rating = data['rating']
                        mentor.save()
                    
                    # Update skills
                    mentor.skills.clear()
                    for skill_name in data['skills']:
                        mentor.skills.add(skill_mapping[skill_name])
                    
                    # Update name if needed
                    if user.get_full_name() != data['full_name']:
                        name_parts = data['full_name'].split()
                        user.first_name = name_parts[0]
                        user.last_name = ' '.join(name_parts[1:])
                        user.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'Updated mentor profile for {username}'))
                    
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User {username} does not exist'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating {username}: {str(e)}'))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _get_category_for_skill(self, skill_name, categories):
        """Determine the appropriate category for a skill"""
        skill_lower = skill_name.lower()
        
        if any(term in skill_lower for term in ['python', 'java', 'programming', 'development']):
            return categories.get('programming')
        elif any(term in skill_lower for term in ['javascript', 'react', 'html', 'css', 'web']):
            return categories.get('web development')
        elif any(term in skill_lower for term in ['data', 'machine learning', 'sql', 'analytics']):
            return categories.get('data science')
        elif any(term in skill_lower for term in ['design', 'ui', 'ux', 'figma', 'adobe']):
            return categories.get('design')
        elif any(term in skill_lower for term in ['business', 'strategy', 'market']):
            return categories.get('business')
        elif any(term in skill_lower for term in ['marketing', 'seo', 'content', 'social media']):
            return categories.get('marketing')
        elif any(term in skill_lower for term in ['education', 'psychology', 'learning']):
            return categories.get('education')
        elif any(term in skill_lower for term in ['health', 'nutrition', 'wellness']):
            return categories.get('health')
        else:
            # Default to programming if no match
            return categories.get('programming') 