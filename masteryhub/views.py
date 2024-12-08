from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import (
    MentorApplicationForm,
    ConcernReportForm,
    BookingForm,
    ReviewForm,
    SessionForm,
    ForumPostForm,
)
from .models import Feedback, Session, Category, Mentorship, Forum, Review, Skill, Mentor, MentorshipRequest
from profiles.models import Profile
import stripe
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


def become_mentor(request):
    """A view that handles the become mentor."""
    if request.method == "POST":
        form = MentorApplicationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            areas_of_expertise = form.cleaned_data["areas_of_expertise"]

            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                from django.contrib.admin.models import LogEntry, ADDITION
                from django.contrib.contenttypes.models import ContentType

                LogEntry.objects.log_action(
                    user_id=admin_user.pk,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=admin_user.pk,
                    object_repr=f"Mentor Application: {name} ({email})",
                    action_flag=ADDITION,
                    change_message=areas_of_expertise,
                )
            messages.success(
                request, "Your mentor application has been submitted successfully.")
            return redirect("home:index")
    else:
        form = MentorApplicationForm()
    return render(request, "masteryhub/become_mentor.html", {"form": form})


def match_mentor_mentee(mentee):
    """A view that handles the mentee-mentor match."""
    mentee_profile = Profile.objects.get(user=mentee)
    mentee_skills = set(mentee_profile.skills.split(","))
    mentee_goals = set(mentee_profile.goals.split(","))

    potential_mentors = Profile.objects.filter(is_expert=True)
    matches = []

    for mentor_profile in potential_mentors:
        mentor_skills = set(mentor_profile.skills.split(","))
        mentor_areas = set(mentor_profile.mentorship_areas.split(","))

        skill_match = mentee_skills & mentor_skills
        goal_match = mentee_goals & mentor_areas

        if skill_match or goal_match:
            matches.append(
                {
                    "mentor": mentor_profile.user,
                    "skill_match": len(skill_match),
                    "goal_match": len(goal_match),
                    "total_match": len(skill_match) + len(goal_match),
                }
            )

    matches.sort(key=lambda x: x["total_match"], reverse=True)
    return matches


def search_mentors(request):
    """A view that handles the mentor searching."""
    query = request.GET.get('q', '')
    selected_skills = request.GET.getlist('skills', [])
    selected_rating = request.GET.get('rating', '')
    available_now = request.GET.get('available_now') == 'true'

    mentors = Mentor.objects.select_related(
        'user').prefetch_related('skills').all()

    print("All mentors before filtering:")
    for mentor in mentors:
        print(
            f"- {mentor.user.first_name} {mentor.user.last_name} ({mentor.user.username})")

    if query:
        print(f"\nSearching for: {query}")
        mentors = mentors.filter(
            Q(user__first_name__icontains=query.split()[0]) |
            Q(user__last_name__icontains=query.split()[-1]) |
            Q(user__username__icontains=query) |
            Q(bio__icontains=query) |
            Q(skills__title__icontains=query)
        ).distinct()

        print("\nFiltered mentors:")
        for mentor in mentors:
            print(f"- {mentor.user.first_name} {mentor.user.last_name}")

    if selected_skills:
        mentors = mentors.filter(skills__id__in=selected_skills).distinct()

    if selected_rating:
        mentors = mentors.filter(rating__gte=float(selected_rating))

    if available_now:
        mentors = mentors.filter(is_available=True)

    skills = Skill.objects.all().order_by('title')

    print(f"\nFinal SQL Query: {mentors.query}")
    print(f"Final Results count: {mentors.count()}")

    context = {
        'mentors': mentors,
        'query': query,
        'skills': skills,
        'selected_skills': selected_skills,
        'selected_rating': selected_rating,
        'available_now': available_now,
    }

    return render(request, 'masteryhub/search_mentors.html', context)


@login_required
def request_mentorship(request, mentor_id):
    """Handle mentorship request."""
    try:
        mentor = User.objects.get(id=mentor_id)

        existing_request = MentorshipRequest.objects.filter(
            mentee=request.user,
            mentor=mentor,
            status__in=['pending', 'accepted']
        ).exists()

        if existing_request:
            messages.warning(
                request, "You already have a pending or active mentorship request with this mentor.")
            return redirect('profiles:mentor_profile', username=mentor.username)

        if request.method == 'POST':
            message = request.POST.get('message', '').strip()

            if not message:
                messages.error(
                    request, "Please provide a message for your mentorship request.")
                return redirect('profiles:mentor_profile', username=mentor.username)

            MentorshipRequest.objects.create(
                mentee=request.user,
                mentor=mentor,
                message=message
            )

            messages.success(
                request, "Your mentorship request has been sent successfully!")
            return redirect('profiles:mentor_profile', username=mentor.username)

        return render(request, 'masteryhub/request_mentorship.html', {
            'mentor': mentor
        })

    except User.DoesNotExist:
        messages.error(request, "Mentor not found.")
        return redirect('masteryhub:mentor_matching')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('masteryhub:mentor_matching')


@login_required
def manage_mentorship_requests(request):
    """A view that handles the mentorship request management."""
    mentor_profile = get_object_or_404(Profile, user=request.user)
    pending_requests = Mentorship.objects.filter(
        mentor=mentor_profile, status="pending")
    return render(request, "masteryhub/manage_mentorship_requests.html", {"pending_requests": pending_requests})


def session_list(request):
    """A view that renders the list of sessions."""
    query = request.GET.get("q")
    selected_category = request.GET.get("category")

    sessions = Session.objects.filter(
        is_active=True,
        status="scheduled",
    ).select_related(
        'host',
        'category',
        'host__user'
    ).prefetch_related('participants')

    print(f"Total sessions found: {sessions.count()}")
    for session in sessions:
        print(f"""
        Session: {session.title}
        Host: {session.host.user.username}
        Category: {session.category}
        Price: {session.price}
        Participants: {session.participants.count()}/{session.max_participants}
        """)

    if query:
        sessions = sessions.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    if selected_category:
        sessions = sessions.filter(category__name=selected_category)

    categories = Category.objects.all()

    user_sessions = []
    if request.user.is_authenticated:
        user_sessions = Session.objects.filter(
            participants=request.user.profile)

    context = {
        "sessions": sessions,
        "categories": categories,
        "selected_category": selected_category,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "user_sessions": user_sessions,
    }

    return render(request, "masteryhub/session_list.html", context)


def list_mentors(request):
    """A view that lists all mentors."""
    query = request.GET.get('q', '')
    areas = request.GET.getlist('areas')
    rating = request.GET.get('rating')
    available_now = request.GET.get('available_now')

    mentors = Profile.objects.filter(is_expert=True)

    if query:
        mentors = mentors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(skills__icontains=query) |
            Q(mentorship_areas__icontains=query)
        ).distinct()

    if areas:
        mentors = mentors.filter(mentorship_areas__id__in=areas).distinct()

    if rating:
        mentors = mentors.filter(rating__gte=rating)

    if available_now:
        mentors = mentors.filter(is_available=True)

    skills = Skill.objects.all()
    categories = Category.objects.all()

    context = {
        'mentors': mentors,
        'skills': skills,
        'categories': categories,
        'query': query,
    }
    return render(request, 'masteryhub/list_mentors.html', context)


@login_required
def mentor_matching_view(request):
    """A view that handles the mentor matching."""
    if request.method == 'POST':
        request.session['mentor_preferences'] = {
            'skills': request.POST.getlist('skills'),
            'experience_level': request.POST.get('experience_level'),
            'availability': request.POST.get('availability') == 'on'
        }
        return redirect('masteryhub:matching_results')

    if 'mentor_preferences' in request.session:
        del request.session['mentor_preferences']

    skills = Skill.objects.all().order_by('title')
    experience_levels = Mentor.EXPERIENCE_LEVELS

    context = {
        'skills': skills,
        'experience_levels': experience_levels,
    }

    return render(request, 'masteryhub/mentor_matching.html', context)


@login_required
def view_session(request, session_id):
    """A view that handles viewing a session."""
    session = get_object_or_404(Session, id=session_id)
    context = {
        "session": session,
        "is_participant": request.user.profile in session.participants.all(),
    }
    return render(request, "masteryhub/view_session.html", context)


@login_required
def create_session(request):
    """A view that handles creating a new session."""
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.host = request.user.profile
            session.save()
            messages.success(request, "Session created successfully.")
            return redirect("masteryhub:view_session", session_id=session.id)
    else:
        form = SessionForm()
    return render(request, "masteryhub/create_session.html", {"form": form})


@login_required
def edit_session(request, session_id):
    """A view that handles editing an existing session."""
    session = get_object_or_404(
        Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("masteryhub:view_session", session_id=session.id)
    else:
        form = SessionForm(instance=session)
    return render(request, "masteryhub/edit_session.html", {"form": form})


@login_required
def delete_session(request, session_id):
    """A view that handles deleting a session."""
    session = get_object_or_404(
        Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        session.delete()
        messages.success(request, "Session deleted successfully.")
        return redirect("masteryhub:session_list")
    return render(request, "masteryhub/delete_session.html", {"session": session})


@login_required
def create_feedback(request, session_id):
    """A view that handles creating feedback for a session."""
    session = get_object_or_404(Session, id=session_id)
    if request.method == "POST":
        feedback_content = request.POST.get("feedback")
        Feedback.objects.create(
            session=session, user=request.user.profile, content=feedback_content)
        messages.success(request, "Thank you for your feedback!")
        return redirect("masteryhub:view_session", session_id=session_id)
    return render(request, "masteryhub/create_feedback.html", {"session": session})


def forum_posts(request):
    """A view that lists all forum posts."""
    posts = Forum.objects.all()
    return render(request, "masteryhub/forum_posts.html", {"posts": posts})


@login_required
def forum_list(request):
    """A view that handles the forum list."""
    categories = Category.objects.all()
    posts = Forum.objects.filter(parent_post=None)
    return render(request, "masteryhub/forum_list.html", {"categories": categories, "posts": posts})


@login_required
def create_forum_post(request):
    """A view that handles creating a forum post."""
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.save()
            messages.success(request, "Forum post created successfully.")
            return redirect("forum_posts")
    else:
        form = ForumPostForm()
    return render(request, "masteryhub/create_forum_post.html", {"form": form})


@login_required
def view_forum_post(request, post_id):
    """A view that handles viewing a forum post."""
    post = get_object_or_404(Forum, id=post_id)
    comments = post.comments.all()
    return render(request, "masteryhub/view_forum_post.html", {"post": post, "comments": comments})


@login_required
def reply_forum_post(request, post_id):
    """A view that handles replying to a forum post."""
    parent_post = get_object_or_404(Forum, id=post_id)
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user.profile
            reply.parent_post = parent_post
            reply.save()
            messages.success(request, "Reply posted successfully.")
            return redirect("masteryhub:view_forum_post", post_id=parent_post.id)
    else:
        form = ForumPostForm()
    return render(request, "masteryhub/reply_forum_post.html", {"form": form, "parent_post": parent_post})


@login_required
def edit_forum_post(request, post_id):
    """A view that handles editing a forum post."""
    post = get_object_or_404(Forum, id=post_id, author=request.user.profile)
    if request.method == "POST":
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Forum post updated successfully.")
            return redirect("forum_posts")
    else:
        form = ForumPostForm(instance=post)
    return render(request, "masteryhub/edit_forum_post.html", {"form": form})


@login_required
def delete_forum_post(request, post_id):
    """A view that handles deleting a forum post."""
    post = get_object_or_404(Forum, id=post_id, author=request.user.profile)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Forum post deleted successfully.")
        return redirect("forum_posts")
    return render(request, "masteryhub/delete_forum_post.html", {"post": post})


def mentor_rules(request):
    """A view that handles the mentor rules."""
    return render(request, "masteryhub/mentor_rules.html")


def mentor_help(request):
    """A view that handles mentor help."""
    return render(request, "masteryhub/mentor_help.html")


def report_concern(request):
    """A view that handles reporting a concern."""
    if request.method == "POST":
        form = ConcernReportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your concern has been reported. We will review it shortly.")
            return redirect("home:index")
    else:
        form = ConcernReportForm()

    return render(request, "masteryhub/report_concern.html", {"form": form})


def book_session(request, session_id):
    """A view that handles booking a session."""
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.session = session
            booking.user = request.user
            booking.booking_date = timezone.now()
            booking.save()
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'masteryhub/book_session.html', {'form': form, 'session': session})


def browse_skills(request):
    """A view to display all skills with optional category filtering."""
    query = request.GET.get("q")
    selected_category = request.GET.get("category")

    skills = Skill.objects.all()

    if query:
        skills = skills.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if selected_category:
        try:
            category_id = int(selected_category)
            skills = skills.filter(category_id=category_id)
        except (ValueError, TypeError):
            skills = skills.filter(category__name=selected_category)

    categories = Category.objects.all()

    skill_sessions = {}
    for skill in skills:
        active_sessions = Session.objects.filter(
            category=skill.category,
            status="scheduled",
            date__gte=timezone.now()
        ).count()
        skill_sessions[skill.id] = active_sessions

    context = {
        "skills": skills,
        "categories": categories,
        "selected_category": selected_category,
        "skill_sessions": skill_sessions,
    }

    return render(request, "masteryhub/browse_skills.html", context)


def review_list(request):
    """A view that lists all reviews."""
    reviews = Review.objects.all()
    return render(request, 'reviews/review_list.html', {'reviews': reviews})


def create_review(request, session_id):
    """A view that handles creating a review for a session."""
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.session = session
            review.reviewer = request.user.profile
            review.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'reviews/create_review.html', {'form': form, 'session': session})


@login_required
def expert_dashboard(request):
    """A view that displays the expert's dashboard with relevant information."""
    profile = get_object_or_404(Profile, user=request.user)

    mentees = Mentorship.objects.filter(mentor=profile)

    upcoming_sessions = Session.objects.filter(
        host=profile, status="scheduled")

    feedbacks = Feedback.objects.filter(session__host=profile)

    context = {
        'profile': profile,
        'mentees': mentees,
        'upcoming_sessions': upcoming_sessions,
        'feedbacks': feedbacks,
    }

    return render(request, 'masteryhub/expert_dashboard.html', context)


@login_required
def mentee_dashboard(request):
    """A view that displays the mentee's dashboard with relevant information."""
    mentee_profile = request.user.profile
    mentorships = Mentorship.objects.filter(mentee=mentee_profile)
    sessions = Session.objects.filter(participants=mentee_profile)

    context = {
        'mentorships': mentorships,
        'sessions': sessions,
    }

    return render(request, 'masteryhub/mentee_dashboard.html', context)


@login_required
def accept_mentorship(request, mentorship_id):
    """A view that allows a mentor to accept a mentorship request."""
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)

    if request.user == mentorship.mentor.user:
        mentorship.status = 'accepted'
        mentorship.save()
        messages.success(request, "Mentorship request accepted successfully.")
    else:
        messages.error(
            request, "You are not authorized to accept this request.")

    return redirect('manage_mentorship_requests')


@login_required
def reject_mentorship(request, mentorship_id):
    """A view that allows a mentor to reject a mentorship request."""
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)

    if request.user == mentorship.mentor.user:
        mentorship.status = 'rejected'
        mentorship.save()
        messages.success(request, "Mentorship request rejected successfully.")
    else:
        messages.error(
            request, "You are not authorized to reject this request.")

    return redirect('manage_mentorship_requests')


@login_required
def my_mentorships(request):
    """A view that displays the user's mentorships."""
    mentorships_as_mentor = Mentorship.objects.filter(
        mentor__user=request.user
    ).select_related('mentee', 'mentor')

    mentorships_as_mentee = Mentorship.objects.filter(
        mentee__user=request.user
    ).select_related('mentee', 'mentor')

    requests_sent = MentorshipRequest.objects.filter(
        mentee=request.user
    ).select_related('mentor')

    requests_received = MentorshipRequest.objects.filter(
        mentor=request.user
    ).select_related('mentee')

    context = {
        'mentorships_as_mentor': mentorships_as_mentor,
        'mentorships_as_mentee': mentorships_as_mentee,
        'requests_sent': requests_sent,
        'requests_received': requests_received,
    }

    return render(request, 'masteryhub/my_mentorships.html', context)


def view_mentor_profile(request, username):
    user = get_object_or_404(User, username=username)
    mentor = get_object_or_404(Mentor, user=user)
    return render(request, 'masteryhub/mentor_profile.html', {'mentor': mentor})


@login_required
def matching_results(request):
    """A view that displays the matching results."""
    try:
        preferences = request.session.get('mentor_preferences', {})

        mentors = Mentor.objects.filter(
            is_available=True,
            user__profile__is_expert=True
        ).exclude(
            user=request.user
        ).select_related(
            'user',
            'user__profile'
        ).prefetch_related('skills')

        if preferences:
            if preferences.get('skills'):
                mentors = mentors.filter(
                    skills__id__in=preferences['skills']
                ).distinct()

            if preferences.get('experience_level'):
                mentors = mentors.filter(
                    experience_level=preferences['experience_level']
                )

            if preferences.get('availability'):
                mentors = mentors.filter(is_available=True)

        matches = []
        for mentor in mentors:
            mentor_skills = set(mentor.skills.values_list('id', flat=True))
            selected_skills = set(map(int, preferences.get('skills', [])))

            if mentor_skills:
                skill_match = (len(selected_skills.intersection(
                    mentor_skills)) / len(mentor_skills)) * 100

                matches.append({
                    'mentor': mentor.user.profile,
                    'skill_match': round(skill_match, 1),
                    'style_match': 75,
                    'availability_match': 80,
                    'total_match': round((skill_match + 75 + 80) / 3, 1)
                })

        matches.sort(key=lambda x: x['total_match'], reverse=True)

        return render(request, 'masteryhub/matching_results.html', {
            'matches': matches[:9],
            'total_matches': len(matches)
        })

    except Exception as e:
        messages.error(
            request, f"An error occurred while finding matches: {str(e)}")
        return render(request, 'masteryhub/matching_results.html', {
            'matches': [],
            'total_matches': 0
        })
