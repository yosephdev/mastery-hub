from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .forms import (
    MentorApplicationForm,
    ConcernReportForm,
    BookingForm,
    ReviewForm,
    SessionForm,
    ForumPostForm,
)
from .models import (
    Feedback, Session, Category, Mentorship, Forum, Review,
    Skill, Mentor, MentorshipRequest, Activity, Order
)
from profiles.models import Profile
import stripe
import logging
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.core.paginator import Paginator

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

    # Get all mentors with their related user and profile data
    mentors = Mentor.objects.select_related(
        'user',
        'user__profile'
    ).prefetch_related('skills').all()

    if query:
        mentors = mentors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(bio__icontains=query) |
            Q(skills__title__icontains=query)
        ).distinct()

    if selected_skills:
        mentors = mentors.filter(skills__id__in=selected_skills).distinct()

    if selected_rating:
        mentors = mentors.filter(rating__gte=float(selected_rating))

    if available_now:
        mentors = mentors.filter(is_available=True)

    skills = Skill.objects.all().order_by('title')

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
def request_mentorship(request, mentor_id=None, profile_id=None):
    """Handle mentorship request."""
    mentor_user = None

    try:
        if profile_id:
            # Get profile and ensure it belongs to a mentor
            profile = get_object_or_404(Profile, id=profile_id)
            # Get or create a mentor record for this user
            mentor, created = Mentor.objects.get_or_create(
                user=profile.user,
                defaults={
                    'bio': profile.bio or '',
                    'is_available': True,
                    'experience_level': 'intermediate',
                    'hourly_rate': 50.00
                }
            )
            mentor_user = profile.user

            # Log the path taken to help with debugging
            logger.info(
                f"Request mentorship via profile_id={profile_id}, found mentor {mentor.id}")

        elif mentor_id:
            # Get mentor directly by ID
            mentor = get_object_or_404(Mentor, id=mentor_id)
            mentor_user = mentor.user

            # Log the path taken to help with debugging
            logger.info(
                f"Request mentorship via mentor_id={mentor_id}, found user {mentor_user.username}")

        else:
            messages.error(
                request, "No mentor or profile specified for mentorship request.")
            return redirect('masteryhub:mentor_matching')

        # Check if the user is requesting mentorship from themselves
        if request.user == mentor_user:
            messages.error(
                request, "You cannot request mentorship from yourself.")
            return redirect('masteryhub:search_mentors')

        # Check if a request already exists
        existing_request = MentorshipRequest.objects.filter(
            mentee=request.user,
            mentor=mentor_user,
            status='pending'
        ).exists()

        if existing_request:
            messages.info(
                request, "You already have a pending request with this mentor.")
            return redirect('profiles:view_mentor_profile', username=mentor_user.username)

        if request.method == 'POST':
            with transaction.atomic():
                message = request.POST.get('message', '').strip()

                if not message:
                    messages.error(
                        request,
                        "Please provide a message for your mentorship request."
                    )
                    if profile_id:
                        return redirect('masteryhub:request_mentorship_profile', profile_id=profile_id)
                    else:
                        return redirect('masteryhub:request_mentorship', mentor_id=mentor_id)

                # Create the mentorship request
                mentorship_request = MentorshipRequest.objects.create(
                    mentee=request.user,
                    mentor=mentor_user,
                    message=message,
                    status='pending'
                )

                # Log the action
                logger.info(
                    f"Created mentorship request {mentorship_request.id} from {request.user.username} to {mentor_user.username}")

                messages.success(
                    request,
                    "Your mentorship request has been sent successfully!"
                )
                return redirect('profiles:view_mentor_profile', username=mentor_user.username)

        context = {
            'mentor': mentor_user,
            'mentor_profile': mentor
        }
        return render(request, 'masteryhub/request_mentorship.html', context)

    except Exception as e:
        logger.error(f"Error in request_mentorship: {str(e)}")
        messages.error(
            request, "An error occurred while processing your request. Please try again.")
        return redirect('masteryhub:search_mentors')


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
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            try:
                session = form.save(commit=False)
                session.host = request.user.profile
                session.save()
                messages.success(request, "Session created successfully.")
                return redirect("masteryhub:view_session", session_id=session.id)
            except Exception as e:
                logger.error(f"Error creating session: {str(e)}")
                messages.error(
                    request, "There was an error creating the session.")
    else:
        form = SessionForm()
    return render(request, "masteryhub/create_session.html", {"form": form})


@login_required
def edit_session(request, session_id):
    session = get_object_or_404(
        Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session updated successfully.")
                return redirect("masteryhub:view_session", session_id=session.id)
            except Exception as e:
                logger.error(f"Error updating session: {str(e)}")
                messages.error(
                    request, "There was an error updating the session.")
    else:
        form = SessionForm(instance=session)
    return render(request, "masteryhub/edit_session.html", {"form": form})


@login_required
def delete_session(request, session_id):
    session = get_object_or_404(
        Session, id=session_id, host=request.user.profile)
    if request.method == "POST":
        try:
            session.delete()
            messages.success(request, "Session deleted successfully.")
            return redirect("masteryhub:session_list")
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            messages.error(request, "There was an error deleting the session.")
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
    """List all forum posts with search and category filtering."""
    posts = Forum.objects.filter(parent_post=None).select_related(
        'author__user', 'category')

    # Search functionality
    q = request.GET.get('q')
    if q:
        posts = posts.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )

    # Category filtering
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    # Get all categories for the filter dropdown
    categories = Category.objects.all()

    # Order by most recent first
    posts = posts.order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 9)  # Show 9 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': category_id,
        'search_query': q,
    }
    return render(request, 'masteryhub/forum_list.html', context)


@login_required
def create_forum_post(request):
    """Create a new forum post."""
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('masteryhub:view_forum_post', post_id=post.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForumPostForm()
    
    return render(request, 'masteryhub/create_forum_post.html', {'form': form})


@login_required
def view_forum_post(request, post_id):
    """View a forum post and its replies."""
    post = get_object_or_404(Forum, id=post_id)
    
    # Get replies with author information
    replies = Forum.objects.filter(parent_post=post).select_related('author__user', 'category')
    
    # Handle reply submission
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user.profile
            reply.parent_post = post
            reply.category = post.category  # Inherit category from parent post
            reply.title = f"Re: {post.title}"  # Set a default title for replies
            reply.save()
            messages.success(request, 'Reply posted successfully!')
            return redirect('masteryhub:view_forum_post', post_id=post.id)
        else:
            # If form is invalid, show the errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ForumPostForm()
    
    context = {
        'post': post,
        'replies': replies,
        'form': form,
        'can_edit': post.can_edit(request.user),
        'comment_permissions': {reply.id: reply.can_edit(request.user) for reply in replies}
    }
    return render(request, 'masteryhub/view_forum_post.html', context)


@login_required
def edit_forum_post(request, post_id):
    """Edit a forum post."""
    post = get_object_or_404(Forum, id=post_id)
    
    if not post.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('masteryhub:forum_list')
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            post.is_edited = True
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('masteryhub:view_forum_post', post_id=post.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForumPostForm(instance=post)
    
    return render(request, 'masteryhub/edit_forum_post.html', {'form': form, 'post': post})


@login_required
def delete_forum_post(request, post_id):
    """Delete a forum post."""
    post = get_object_or_404(Forum, id=post_id)
    
    if not post.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('masteryhub:forum_list')
    
    if request.method == 'POST':
        # Check if it's a reply or a main post
        is_reply = post.parent_post is not None
        post.delete()
        
        if is_reply:
            messages.success(request, 'Reply deleted successfully!')
        else:
            messages.success(request, 'Post deleted successfully!')
            
        return redirect('masteryhub:forum_list')
    
    return render(request, 'masteryhub/delete_forum_post.html', {'post': post})


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
            return redirect('masteryhub:booking_success')
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
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        user_profile = None

    context = {
        'upcoming_sessions': Session.objects.filter(
            participants=user_profile,
            date__gte=timezone.now()
        ).order_by('date')[:5] if user_profile else [],

        'booked_sessions': Session.objects.filter(
            participants=user_profile
        ).order_by('-date') if user_profile else [],

        'recent_activities': [],
    }

    try:
        context['recent_activities'] = Activity.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:5]
    except:
        pass

    return render(request, 'masteryhub/mentee_dashboard.html', context)


@login_required
def accept_mentorship(request, mentorship_id):
    try:
        mentorship_request = get_object_or_404(
            MentorshipRequest, id=mentorship_id)

        if request.user != mentorship_request.mentor:
            messages.error(
                request, "You are not authorized to accept this request.")
            return redirect('masteryhub:my_mentorships')

        with transaction.atomic():
            mentor_profile = request.user.profile

            try:
                mentee_profile = Profile.objects.get(
                    user=mentorship_request.mentee)
            except Profile.DoesNotExist:
                mentee_profile = Profile.objects.create(
                    user=mentorship_request.mentee)

            mentorship, created = Mentorship.objects.get_or_create(
                mentor=mentor_profile,
                mentee=mentee_profile,
                defaults={
                    'status': 'active',
                    'start_date': timezone.now().date(),
                    'goals': mentorship_request.message,
                }
            )

            if not created:
                mentorship.status = 'active'
                mentorship.start_date = timezone.now().date()
                mentorship.goals = mentorship_request.message
                mentorship.save()

            mentorship_request.status = 'accepted'
            mentorship_request.save()

            try:
                Activity.objects.create(
                    user=request.user,
                    activity_type='MENTORSHIP_ACCEPTED',
                    content_object=mentorship
                )
            except Exception as e:
                logger.warning(f"Failed to create activity log: {str(e)}")

            messages.success(
                request, "Mentorship request accepted successfully.")
            return redirect('masteryhub:my_mentorships')

    except MentorshipRequest.DoesNotExist:
        mentorship = get_object_or_404(Mentorship, id=mentorship_id)

        if request.user == mentorship.mentor.user:
            mentorship.status = 'active'
            mentorship.start_date = timezone.now().date()
            mentorship.save()
            messages.success(request, "Mentorship accepted successfully.")
        else:
            messages.error(
                request, "You are not authorized to accept this request.")

        return redirect('masteryhub:my_mentorships')

    except Exception as e:
        logger.error(f"Error accepting mentorship: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('masteryhub:my_mentorships')


@login_required
def reject_mentorship(request, mentorship_id):
    try:
        mentorship_request = get_object_or_404(
            MentorshipRequest, id=mentorship_id)

        if request.user != mentorship_request.mentor:
            messages.error(
                request, "You are not authorized to reject this request.")
            return redirect('masteryhub:my_mentorships')

        mentorship_request.status = 'rejected'
        mentorship_request.save()

        messages.success(request, "Mentorship request rejected successfully.")
        return redirect('masteryhub:my_mentorships')

    except MentorshipRequest.DoesNotExist:
        mentorship = get_object_or_404(Mentorship, id=mentorship_id)

        if request.user == mentorship.mentor.user:
            mentorship.status = 'rejected'
            mentorship.save()
            messages.success(request, "Mentorship rejected successfully.")
        else:
            messages.error(
                request, "You are not authorized to reject this request.")

        return redirect('masteryhub:my_mentorships')

    except Exception as e:
        logger.error(f"Error rejecting mentorship: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('masteryhub:my_mentorships')


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


@login_required
def view_mentor_profile(request, username):
    try:
        mentor = Mentor.objects.get(user__username__iexact=username)
    except Mentor.DoesNotExist:
        return render(request, 'profiles/mentor_not_found.html', status=404)

    context = {
        'profile': mentor,
        'is_own_profile': request.user.username == username,
    }
    return render(request, 'profiles/view_mentor_profile.html', context)


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
                    'mentor': mentor,
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


def booking_success(request):
    """A view that displays the booking success page."""
    return render(request, 'masteryhub/booking_success.html')


@login_required
def enroll_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    try:
        profile = request.user.profile
        print(f"Found profile: {profile.id}")
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        print(f"Created new profile: {profile.id}")
        messages.info(request, "A new profile was created for you.")

    try:
        session.participants.add(profile)
        session.save()
        messages.success(
            request, "You have successfully enrolled in this session!")
    except Exception as e:
        print(f"Error details: {str(e)}")
        messages.error(request, f"An error occurred while enrolling: {str(e)}")

    return redirect('masteryhub:view_session', session_id=session.id)


@login_required
def cancel_mentorship_request(request, request_id):
    """A view that allows a mentee to cancel a pending mentorship request."""
    try:
        mentorship_request = get_object_or_404(
            MentorshipRequest, id=request_id)

        # Check authorization (only the mentee can cancel their request)
        if request.user != mentorship_request.mentee:
            messages.error(
                request, "You are not authorized to cancel this request.")
            return redirect('masteryhub:my_mentorships')

        # Only allow cancellation if the request is still pending
        if mentorship_request.status != 'pending':
            messages.error(
                request, "This request cannot be cancelled as it's no longer pending.")
            return redirect('masteryhub:my_mentorships')

        # Update request status
        mentorship_request.status = 'cancelled'
        mentorship_request.save()

        # Log the action
        logger.info(
            f"Mentorship request {request_id} cancelled by {request.user.username}")

        messages.success(request, "Mentorship request cancelled successfully.")
    except Exception as e:
        logger.error(f"Error cancelling mentorship request: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('masteryhub:my_mentorships')


@login_required
def my_orders(request):
    orders = request.user.checkout_orders.all().order_by('-date')
    return render(request, 'masteryhub/my_orders.html', {'orders': orders})


@login_required
def my_learning(request):
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        user_profile = None

    context = {
        'upcoming_sessions': Session.objects.filter(
            participants=user_profile,
            date__gte=timezone.now()
        ).order_by('date')[:5] if user_profile else [],

        'booked_sessions': Session.objects.filter(
            participants=user_profile
        ).order_by('-date') if user_profile else [],

        'recent_activities': Activity.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:5] if user_profile else [],

        'orders': Order.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    }

    return render(request, 'masteryhub/my_learning.html', context)
