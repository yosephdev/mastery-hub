from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import MentorApplicationForm, ConcernReportForm, BookingForm, ReviewForm, SessionForm, ForumPostForm
from .models import Feedback, Session, Category, Mentorship, Forum
from profiles.models import Profile
import stripe
import json
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


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
                LogEntry.objects.log_action(
                    user_id=admin_user.pk,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=admin_user.pk,
                    object_repr=f"Mentor Application: {name} ({email})",
                    action_flag=ADDITION,
                    change_message=areas_of_expertise,
                )
            messages.success(request, "Your mentor application has been submitted successfully.")
            return redirect("home")
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
    query = request.GET.get("q")
    mentors = Profile.objects.filter(is_expert=True)
    if query:
        mentors = mentors.filter(mentorship_areas__icontains=query)

    print(f"Query: {query}, Mentors Count: {mentors.count()}")  

    return render(request, "masteryhub/search_mentors.html", {"mentors": mentors, "query": query})


@login_required
def request_mentorship(request, mentor_id):
    """A view that handles the mentorship request."""
    mentor_user = get_object_or_404(User, id=mentor_id)
    mentor_profile = get_object_or_404(Profile, user=mentor_user)
    mentee_profile = get_object_or_404(Profile, user=request.user)

    if not mentor_profile.is_available:
        messages.error(request, f"{mentor_user.username} is not currently accepting mentorship requests.")
        return redirect("view_mentor_profile", username=mentor_user.username)

    if request.method == "POST":
        mentorship, created = Mentorship.objects.get_or_create(
            mentor=mentor_profile, mentee=mentee_profile, status="pending"
        )    
        if created:
            message = f"Mentorship request sent to {mentor_user.username}"
        else:
            message = f"You already have a pending request with {mentor_user.username}"

        messages.success(request, message)
        return redirect("view_mentor_profile", username=mentor_user.username)

    return render(request, "masteryhub/request_mentorship.html", {"mentor": mentor_user})


@login_required
def manage_mentorship_requests(request):
    """A view that handles the mentorship request management."""
    mentor_profile = get_object_or_404(Profile, user=request.user)
    pending_requests = Mentorship.objects.filter(mentor=mentor_profile, status="pending")
    return render(request, "masteryhub/manage_mentorship_requests.html", {"pending_requests": pending_requests})


def session_list(request):
    """A view that renders the list of sessions with optional filtering."""
    query = request.GET.get("q")
    selected_category = request.GET.get("category")

    sessions = Session.objects.filter(status="scheduled")

    if query:
        sessions = sessions.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if selected_category:
        sessions = sessions.filter(category__name=selected_category)

    categories = Category.objects.all()

    for session in sessions:
        print(f"Session ID: {session.id}, Price: {session.price}")

    context = {
        "sessions": sessions,
        "categories": categories,
        "selected_category": selected_category,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "masteryhub/session_list.html", context)


def list_mentors(request):
    """A view that handles the mentor list."""
    query = request.GET.get("q")
    if query:
        mentors = Profile.objects.filter(is_expert=True).filter(
            Q(user__username__icontains=query) | Q(mentorship_areas__icontains=query)
        )
    else:
        mentors = Profile.objects.filter(is_expert=True)
    return render(request, "masteryhub/list_mentors.html", {"mentors": mentors, "query": query})


@login_required
def mentor_matching_view(request):
    """A view that handles the mentor matching."""
    if request.user.is_authenticated:
        mentee = request.user
        matches = match_mentor_mentee(mentee)        
        return render(request, "masteryhub/mentor_matching.html", {"matches": matches})

    return redirect("home")


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
            return redirect("view_session", session_id=session.id)
    else:
        form = SessionForm()
    return render(request, "masteryhub/create_session.html", {"form": form})


@login_required
def edit_session(request, session_id):
    """A view that handles editing an existing session."""
    session = get_object_or_404(Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("view_session", session_id=session.id)
    else:
        form = SessionForm(instance=session)
    return render(request, "masteryhub/edit_session.html", {"form": form})


@login_required
def delete_session(request, session_id):
    """A view that handles deleting a session."""
    session = get_object_or_404(Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        session.delete()
        messages.success(request, "Session deleted successfully.")
        return redirect("session_list")
    return render(request, "masteryhub/delete_session.html", {"session": session})


@login_required
def create_feedback(request, session_id):
    """A view that handles creating feedback for a session."""
    session = get_object_or_404(Session, id=session_id)
    if request.method == "POST":
        feedback_content = request.POST.get("feedback")
        Feedback.objects.create(session=session, user=request.user.profile, content=feedback_content)
        messages.success(request, "Thank you for your feedback!")
        return redirect("view_session", session_id=session_id)
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
            return redirect("view_forum_post", post_id=parent_post.id)
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
            messages.success(request, "Your concern has been reported. We will review it shortly.")
            return redirect("home")
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
            booking.user = request.user  
            booking.save()
            return redirect('booking_success')  
    else:
        form = BookingForm()

    return render(request, 'masteryhub/book_session.html', {'form': form, 'session': session})


def browse_skills_view(request):   
    """A view that handles browsing skills."""
    return render(request, 'masteryhub/browse_skills.html')  


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