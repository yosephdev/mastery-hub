from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
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
    MentorshipRequestForm
)
from .models import Feedback, Session, Category, Mentorship, Forum, Review, Skill, Mentor, MentorshipRequest
from profiles.models import Profile
import stripe
import logging
from django.contrib.auth import get_user_model
from django.http import JsonResponse

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
        mentor = get_object_or_404(User, id=mentor_id)
        mentor_profile = get_object_or_404(
            Profile, user=mentor, is_expert=True)

        if request.user == mentor:
            messages.error(
                request, "You cannot request mentorship from yourself.")
            return redirect('masteryhub:list_mentors')

        existing_request = MentorshipRequest.objects.filter(
            mentee=request.user,
            mentor=mentor,
            status='pending'
        ).exists()

        if existing_request:
            messages.warning(
                request,
                "You already have a pending request with this mentor."
            )
            return redirect('masteryhub:list_mentors')

        if request.method == 'POST':
            form = MentorshipRequestForm(request.POST)
            if form.is_valid():
                mentorship_request = form.save(commit=False)
                mentorship_request.mentee = request.user
                mentorship_request.mentor = mentor
                mentorship_request.save()

                messages.success(
                    request,
                    f"Mentorship request sent to {mentor.username}!"
                )
                return redirect('masteryhub:mentee_dashboard')
        else:
            form = MentorshipRequestForm()

        context = {
            'form': form,
            'mentor': mentor,
            'mentor_profile': mentor_profile
        }
        return render(request, 'masteryhub/request_mentorship.html', context)

    except User.DoesNotExist:
        messages.error(
            request,
            "The mentor you're trying to reach doesn't exist anymore."
        )
        return redirect('masteryhub:list_mentors')
    except Profile.DoesNotExist:
        messages.error(
            request,
            "This user is not registered as a mentor."
        )
        return redirect('masteryhub:list_mentors')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('masteryhub:list_mentors')


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
    """A view that handles mentor matching based on multiple criteria."""
    categories = Category.objects.all()
    skills = Skill.objects.all()

    if request.method == 'POST':
        learning_goal = request.POST.get('learning_goal')
        experience_level = request.POST.get('experience_level')
        learning_style = request.POST.get('learning_style')
        availability = request.POST.get('availability')
        budget = request.POST.get('budget')

        mentors = Profile.objects.filter(is_expert=True).annotate(
            student_count=Count('mentorships_as_mentor')
        )

        budget_ranges = {
            'low': (0, 50),
            'medium': (51, 100),
            'high': (101, 1000)
        }
        if budget in budget_ranges:
            min_price, max_price = budget_ranges[budget]
            mentors = mentors.filter(
                user__skills__price__range=(min_price, max_price)
            ).distinct()

        if learning_goal:
            mentors = mentors.filter(
                Q(sessions_hosted__category_id=learning_goal) |
                Q(user__skills__category=learning_goal)
            ).distinct()

        matched_mentors = []
        for mentor in mentors:
            mentor_reviews = Review.objects.filter(
                session__host=mentor
            ).aggregate(avg_rating=Avg('rating'))
            avg_rating = mentor_reviews['avg_rating'] or 0

            relevant_skills = mentor.user.skills.filter(
                category=learning_goal).count() if learning_goal else 0
            total_skills = mentor.user.skills.count()
            skill_match = (relevant_skills / total_skills *
                           100) if total_skills > 0 else 0

            match_score = {
                'mentor': mentor,
                'skill_match': skill_match,
                'style_match': 80,
                'availability_match': 90,
                'rating_score': (avg_rating / 5) * 100
            }

            total_match = (
                match_score['skill_match'] * 0.35 +
                match_score['style_match'] * 0.25 +
                match_score['availability_match'] * 0.20 +
                match_score['rating_score'] * 0.20
            )

            matched_mentors.append({
                'mentor': mentor,
                'total_match': round(total_match, 1),
                'skill_match': round(match_score['skill_match']),
                'style_match': match_score['style_match'],
                'availability_match': match_score['availability_match']
            })

        matched_mentors.sort(key=lambda x: x['total_match'], reverse=True)

        return render(request, 'masteryhub/matching_results.html', {
            'matches': matched_mentors[:10],
            'form_submitted': True
        })

    context = {
        'categories': categories,
        'skills': skills,
        'experience_levels': [
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        'learning_styles': [
            ('hands_on', 'Hands-on Practice'),
            ('theoretical', 'Theoretical Learning'),
            ('mixed', 'Mixed Approach')
        ],
        'availability_options': [
            ('weekdays', 'Weekdays'),
            ('weekends', 'Weekends'),
            ('flexible', 'Flexible')
        ],
        'budget_ranges': [
            ('low', '$20-50'),
            ('medium', '$51-100'),
            ('high', '$101+')
        ]
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
    """A view that displays the current user's mentorships."""
    mentorships = Mentorship.objects.filter(mentee=request.user.profile)

    context = {
        'mentorships': mentorships,
    }

    return render(request, 'masteryhub/my_mentorships.html', context)


def view_mentor_profile(request, username):
    user = get_object_or_404(User, username=username)
    mentor = get_object_or_404(Mentor, user=user)
    return render(request, 'masteryhub/mentor_profile.html', {'mentor': mentor})
