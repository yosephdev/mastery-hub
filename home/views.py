import logging

from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from masteryhub.models import Session, Category
from profiles.models import Profile
from .forms import ContactForm
from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from decimal import Decimal

logger = logging.getLogger(__name__)

User = get_user_model()


def create_default_sessions():
    """
    Seed the database with demo sessions if none exist.
    Uses get_or_create throughout to remain idempotent.
    Note: a superuser must already exist before this is called,
    or the sessions will simply be skipped.
    """
    categories = {
        'Technology': Category.objects.get_or_create(name='Technology')[0],
        'Marketing': Category.objects.get_or_create(name='Marketing')[0],
        'Data Science': Category.objects.get_or_create(name='Data Science')[0],
    }

    try:
        default_host = Profile.objects.first()
        if not default_host:
            logger.warning(
                "No Profile found – skipping default session creation. "
                "Create at least one user via the admin panel first."
            )
            return
    except Exception as e:
        logger.error("Error fetching default host for demo sessions: %s", e)
        return

    default_sessions = [
        {
            'title': 'Introduction to Web Development',
            'description': 'Learn the basics of HTML, CSS, and JavaScript',
            'category': categories['Technology'],
            'price': Decimal('99.99'),
            'max_participants': 20,
        },
        {
            'title': 'Advanced React Development',
            'description': 'Master React.js and build modern web applications',
            'category': categories['Technology'],
            'price': Decimal('149.99'),
            'max_participants': 15,
        },
        {
            'title': 'Digital Marketing Fundamentals',
            'description': 'Learn essential digital marketing strategies',
            'category': categories['Marketing'],
            'price': Decimal('79.99'),
            'max_participants': 25,
        },
        {
            'title': 'Social Media Marketing',
            'description': 'Master social media marketing campaigns',
            'category': categories['Marketing'],
            'price': Decimal('89.99'),
            'max_participants': 20,
        },
        {
            'title': 'Python for Data Science',
            'description': 'Learn Python programming for data analysis',
            'category': categories['Data Science'],
            'price': Decimal('129.99'),
            'max_participants': 15,
        },
        {
            'title': 'Machine Learning Basics',
            'description': 'Introduction to machine learning algorithms',
            'category': categories['Data Science'],
            'price': Decimal('159.99'),
            'max_participants': 12,
        },
    ]

    # Create sessions
    for session_data in default_sessions:
        Session.objects.get_or_create(
            title=session_data['title'],
            defaults={
                'description': session_data['description'],
                'category': session_data['category'],
                'host': default_host,
                'price': session_data['price'],
                'max_participants': session_data['max_participants'],
                'is_active': True,
            }
        )


def index(request):
    """
    A view to return the index page for the home app
    """
    if Session.objects.count() == 0:
        create_default_sessions()

    social_auth_google_enabled = SocialApp.objects.filter(
        provider='google').exists()

    slides = [
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-1.webp',
            'alt': 'Slide 1',
            'heading': 'Welcome to Skill Sharing',
            'caption': 'Learn new skills from experts.',
            'button_url': '/about/',
            'button_text': 'Learn More',
            'button_class': 'btn-primary'
        },
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-2.webp',
            'alt': 'Slide 2',
            'heading': 'Join Our Community',
            'caption': 'Connect with mentors and peers.',
            'button_url': '/accounts/signup/',
            'button_text': 'Join Now',
            'button_class': 'btn-warning'
        },
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-3.webp',
            'alt': 'Slide 3',
            'heading': 'Upskill Today',
            'caption': 'Enhance your career with new skills.',
            'button_url': '/accounts/signup/',
            'button_text': 'Get Started',
            'button_class': 'btn-success'
        },
    ]

    mentors = [
        {
            'name': 'Anna Carolina',
            'username': 'Anna',
            'field': 'Health & Wellness',
            'specialty': 'Nutrition Expert',
            'image': {'url': f'https://avatar.iran.liara.run/public/girl?username=Anna_Carolina'},
            'rating': 4.9,
            'students_count': 1234,
            'sessions_count': 89,
            'description': 'Certified nutritionist with 10+ years of experience'
        },
        {
            'name': 'Sara Taye',
            'username': 'Sara',
            'field': 'Business',
            'specialty': 'Business Strategy',
            'image': {'url': f'https://eu.ui-avatars.com/api/?name=Sara+Taye&size=250&background=random'},
            'rating': 4.8,
            'students_count': 956,
            'sessions_count': 67,
            'description': 'MBA, Former CEO with expertise in business growth'
        },
        {
            'name': 'Kidist Shibre',
            'username': 'Kidist',
            'field': 'Education',
            'specialty': 'Educational Psychology',
            'image': {'url': f'https://robohash.org/Kidist_Shibre'},
            'rating': 4.9,
            'students_count': 1567,
            'sessions_count': 124,
            'description': 'PhD in Educational Psychology, 15+ years teaching experience'
        },
        {
            'name': 'Alex Jacob',
            'username': 'Alex',
            'field': 'Technology',
            'specialty': 'Software Development',
            'image': {'url': f'https://avatar.iran.liara.run/public/boy?username=Alex_Jacob'},
            'rating': 4.7,
            'students_count': 2341,
            'sessions_count': 156,
            'description': 'Senior Software Engineer, Full-stack development expert'
        },
        {
            'name': 'Maria Rodriguez',
            'username': 'Maria',
            'field': 'Design',
            'specialty': 'UX/UI Design',
            'image': {'url': f'https://eu.ui-avatars.com/api/?name=Maria+Rodriguez&size=250'},
            'rating': 4.8,
            'students_count': 1789,
            'sessions_count': 98,
            'description': 'Lead Designer at top tech company, 8+ years experience',
            'is_demo': True
        },
        {
            'name': 'John Smith',
            'username': 'John',
            'field': 'Marketing',
            'specialty': 'Digital Marketing',
            'image': {'url': f'https://avatar.iran.liara.run/public/boy?username=John'},
            'rating': 4.6,
            'students_count': 2156,
            'sessions_count': 134,
            'description': 'Digital Marketing Strategist, Google certified expert',
            'is_demo': True
        },
        {
            'name': 'Lisa Chen',
            'username': 'Lisa',
            'field': 'Finance',
            'specialty': 'Investment Banking',
            'image': {'url': f'https://robohash.org/Lisa_Chen'},
            'rating': 4.9,
            'students_count': 876,
            'sessions_count': 45,
            'description': 'Former Investment Banker, CFA charterholder',
            'is_demo': True
        },
        {
            'name': 'David Kumar',
            'username': 'David',
            'field': 'Data Science',
            'specialty': 'Machine Learning',
            'image': {'url': f'https://eu.ui-avatars.com/api/?name=David+Kumar&size=250&background=random'},
            'rating': 4.8,
            'students_count': 1654,
            'sessions_count': 87,
            'description': 'AI Researcher, PhD in Machine Learning',
            'is_demo': True
        }
    ]

    testimonials = [
        {
            'name': 'Emily Rodriguez',
            'role': 'UX Designer',
            'image': {'url': f'https://eu.ui-avatars.com/api/?name=Emily+Rodriguez&size=250&background=random'},
            'text': 'MasteryHub has transformed my career! The mentors are incredibly knowledgeable and supportive. I went from a junior designer to leading my own team in just 8 months.',
            'rating': 5
        },
        {
            'name': 'Michael Thompson',
            'role': 'Software Developer',
            'image': {'url': f'https://avatar.iran.liara.run/public/boy?username=Michael'},
            'text': "I've learned so much in such a short time. The platform is easy to use and the sessions are very engaging. The practical projects helped me build a strong portfolio.",
            'rating': 5
        },
        {
            'name': 'Sarah Johnson',
            'role': 'Marketing Manager',
            'image': {'url': f'https://robohash.org/Sarah_Johnson'},
            'text': 'The personalized mentorship program exceeded my expectations. My mentor provided invaluable insights that helped me secure a promotion at work.',
            'rating': 5
        },
        {
            'name': 'James Wilson',
            'role': 'Business Analyst',
            'image': {'url': f'https://eu.ui-avatars.com/api/?name=James+Wilson&size=250&background=random'},
            'text': 'Outstanding platform for professional development. The mentors are industry experts who provide practical, real-world advice and guidance.',
            'rating': 5
        },
        {
            'name': 'Anna Martinez',
            'role': 'Data Scientist',
            'image': {'url': f'https://avatar.iran.liara.run/public/girl?username=Anna'},
            'text': 'The quality of instruction is exceptional. I particularly appreciated the hands-on projects and personalized feedback from my mentor.',
            'rating': 5
        },
        {
            'name': 'Robert Chen',
            'role': 'Product Manager',
            'image': {'url': f'https://robohash.org/Robert_Chen'},
            'text': 'MasteryHub helped me transition into product management seamlessly. The structured learning path and expert guidance were invaluable.',
            'rating': 5
        }
    ]

    categories = [
        {
            'name': 'Technology',
            'icon': 'fas fa-laptop-code',
            'color': 'primary',
            'count': 150
        },
        {
            'name': 'Business',
            'icon': 'fas fa-chart-line',
            'color': 'success',
            'count': 120
        },
        {
            'name': 'Design',
            'icon': 'fas fa-paint-brush',
            'color': 'info',
            'count': 80
        },
        {
            'name': 'Marketing',
            'icon': 'fas fa-bullhorn',
            'color': 'warning',
            'count': 90
        },
        {
            'name': 'Data Science',
            'icon': 'fas fa-database',
            'color': 'danger',
            'count': 70
        },
        {
            'name': 'Personal Development',
            'icon': 'fas fa-brain',
            'color': 'secondary',
            'count': 100
        }
    ]

    web_dev_sessions = Session.objects.filter(
        category__name='Technology',
        is_active=True
    ).order_by('-created_at')[:3]

    digital_marketing_sessions = Session.objects.filter(
        category__name='Marketing',
        is_active=True
    ).order_by('-created_at')[:3]

    data_science_sessions = Session.objects.filter(
        category__name='Data Science',
        is_active=True
    ).order_by('-created_at')[:3]

    context = {
        'slides': slides,
        'mentors': mentors,
        'testimonials': testimonials,
        'categories': categories,
        'featured_mentors': mentors[:4],
        'featured_testimonials': testimonials[:3],
        'social_auth_google_enabled': social_auth_google_enabled,
        'web_dev_sessions': web_dev_sessions,
        'digital_marketing_sessions': digital_marketing_sessions,
        'data_science_sessions': data_science_sessions,
    }

    return render(request, "home/index.html", context)


def about(request):
    """A view that handles the about page."""
    return render(request, "home/about.html")


def contact(request):
    """Handle the contact page and form submission."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message_body = form.cleaned_data["message"]

            try:
                send_mail(
                    f"Message from {name} via MasteryHub",
                    message_body,
                    email,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "Thank you! Your message has been sent successfully."
                )
            except BadHeaderError:
                messages.error(request, "Invalid header found. Please try again.")
            except Exception as e:
                logger.error("Contact form email error: %s", e)
                messages.error(
                    request,
                    "Sorry, we could not send your message. Please try again later."
                )
            return redirect("home:contact")
    else:
        form = ContactForm()

    return render(request, "home/contact.html", {"form": form})


def search(request):
    """Handle site-wide search for mentors and sessions."""
    query = request.GET.get("q", "").strip()
    profiles = []
    sessions = []
    no_results = False

    if query:
        try:
            profiles = list(
                Profile.objects.filter(
                    Q(user__username__icontains=query)
                    | Q(user__first_name__icontains=query)
                    | Q(user__last_name__icontains=query)
                    | Q(skills__icontains=query)
                ).select_related("user")
            )
            sessions = list(
                Session.objects.filter(
                    Q(title__icontains=query) | Q(description__icontains=query),
                    is_active=True,
                ).select_related("host", "category")
            )
            no_results = not profiles and not sessions
        except Exception as e:
            logger.error("Search error for query '%s': %s", query, e)
            messages.error(request, "An error occurred. Please try again.")

    context = {
        "query": query,
        "profiles": profiles,
        "sessions": sessions,
        "no_results": no_results,
    }
    return render(request, "home/search_results.html", context)
