from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from masteryhub.models import Mentorship, Session
from profiles.models import Profile
from .forms import ContactForm

# Create your views here.


def index(request):
    """
    A view to return the index page for the home app
    """
    return render(request, "home/index.html")


def home(request):
    """A view that handles the home page."""
    return render(request, "home/index.html")


def about(request):
    """A view that handles the about page."""
    return render(request, "home/about.html")


def contact(request):
    """A view that handles the contact page."""
    return render(request, "home/contact.html")


def contact_view(request):
    """A view that handles the contact form submission."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            try:
                send_mail(
                    f"Message from {name} via MasteryHub",
                    message,
                    email,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            except Exception as e:
                return HttpResponse(f"Error sending email: {e}")

            request.session["message_sent"] = True
            return redirect("home:contact")
    else:
        form = ContactForm()

    message_sent = request.session.pop("message_sent", False)

    return render(
        request,
        "home/contact.html",
        {"form": form, "message_sent": message_sent},
    )


def search(request):
    """A view that handles search functionality."""
    query = request.GET.get("q", "").strip()
    profiles = []
    sessions = []
    error_message = ""

    if query:
        try:
            profiles = Profile.objects.filter(
                Q(user__username__icontains=query) | Q(skills__icontains=query)
            )
            sessions = Session.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

            if not profiles and not sessions:
                error_message = "No results found for your search."
        except Exception as e:
            error_message = f"An error occurred during the search: {str(e)}"
    else:
        error_message = "Please enter a search term."

    context = {
        "query": query,
        "profiles": profiles,
        "sessions": sessions,
        "error_message": error_message,
    }
    return render(request, "home/search_results.html", context)


def home_view(request):
    """A view that handles the home page content including carousel, mentors, and testimonials."""
    slides = [
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-1.webp',
            'alt': 'Slide 1',
            'heading': 'Welcome to Skill Sharing',
            'caption': 'Learn new skills from experts.',
            'button_url': '/learn-more/',
            'button_text': 'Learn More',
            'button_class': 'btn-primary'
        },
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-2.webp',
            'alt': 'Slide 2',
            'heading': 'Join Our Community',
            'caption': 'Connect with mentors and peers.',
            'button_url': '/join/',
            'button_text': 'Join Now',
            'button_class': 'btn-warning'
        },
        {
            'image': 'https://skill-sharing.s3.amazonaws.com/static/images/hero-bg-3.webp',
            'alt': 'Slide 3',
            'heading': 'Upskill Today',
            'caption': 'Enhance your career with new skills.',
            'button_url': '/upskill/',
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
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/anna-carolina.webp'},
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
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/sara-taye.webp'},
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
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/kidist-shibre.webp'},
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
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/alex-jacob.webp'},
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
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/maria-rodriguez.webp'},
            'rating': 4.8,
            'students_count': 1789,
            'sessions_count': 98,
            'description': 'Lead Designer at top tech company, 8+ years experience'
        },
        {
            'name': 'John Smith',
            'username': 'John',
            'field': 'Marketing',
            'specialty': 'Digital Marketing',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/john-smith.webp'},
            'rating': 4.6,
            'students_count': 2156,
            'sessions_count': 134,
            'description': 'Digital Marketing Strategist, Google certified expert'
        },
        {
            'name': 'Lisa Chen',
            'username': 'Lisa',
            'field': 'Finance',
            'specialty': 'Investment Banking',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/lisa-chen.webp'},
            'rating': 4.9,
            'students_count': 876,
            'sessions_count': 45,
            'description': 'Former Investment Banker, CFA charterholder'
        },
        {
            'name': 'David Kumar',
            'username': 'David',
            'field': 'Data Science',
            'specialty': 'Machine Learning',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/david-kumar.webp'},
            'rating': 4.8,
            'students_count': 1654,
            'sessions_count': 87,
            'description': 'AI Researcher, PhD in Machine Learning'
        }
    ]

    testimonials = [
        {
            'name': 'Emily Rodriguez',
            'role': 'UX Designer',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial1.webp'},
            'text': 'MasteryHub has transformed my career! The mentors are incredibly knowledgeable and supportive. I went from a junior designer to leading my own team in just 8 months.',
            'rating': 5
        },
        {
            'name': 'Michael Thompson',
            'role': 'Software Developer',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial2.webp'},
            'text': "I've learned so much in such a short time. The platform is easy to use and the sessions are very engaging. The practical projects helped me build a strong portfolio.",
            'rating': 5
        },
        {
            'name': 'Sarah Johnson',
            'role': 'Marketing Manager',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial3.webp'},
            'text': 'The personalized mentorship program exceeded my expectations. My mentor provided invaluable insights that helped me secure a promotion at work.',
            'rating': 5
        },
        {
            'name': 'James Wilson',
            'role': 'Business Analyst',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial4.webp'},
            'text': 'Outstanding platform for professional development. The mentors are industry experts who provide practical, real-world advice and guidance.',
            'rating': 5
        },
        {
            'name': 'Anna Martinez',
            'role': 'Data Scientist',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial5.webp'},
            'text': 'The quality of instruction is exceptional. I particularly appreciated the hands-on projects and personalized feedback from my mentor.',
            'rating': 5
        },
        {
            'name': 'Robert Chen',
            'role': 'Product Manager',
            'image': {'url': 'https://skill-sharing.s3.amazonaws.com/static/images/testimonial6.webp'},
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

    context = {
        'slides': slides,
        'mentors': mentors,
        'testimonials': testimonials,
        'categories': categories,
        'featured_mentors': mentors[:4],
        'featured_testimonials': testimonials[:3],
    }

    return render(request, 'home/index.html', context)
