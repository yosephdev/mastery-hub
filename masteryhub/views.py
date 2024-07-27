from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Count, Sum
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import MentorApplicationForm, ConcernReportForm
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import (
    Profile,
    Feedback,
    Session,
    Category,
    Mentorship,
    Payment,
    Cart,
    CartItem,
    Order,
)
from .forms import OrderForm
import stripe
import json
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

from .forms import (
    CustomSignupForm,
    CustomUserChangeForm,
    ProfileForm,
    SessionForm,
    ForumPostForm,
    MentorApplicationForm,
)
from .models import Profile, Mentorship, Session, Forum, Category, Feedback


def home(request):
    """A view that handles the home page."""
    return render(request, "masteryhub/index.html")


def signup_view(request):
    """A view that handles the sign up."""
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, f"Welcome, {user.username}! Registration successful!"
            )
            return redirect("home")
        for field, error in form.errors.items():
            messages.error(request, f"{field}: {error}")
    else:
        form = CustomSignupForm()
    return render(request, "account/signup.html", {"form": form})


class CustomLoginView(LoginView):
    """A view that handles the login."""

    template_name = "account/login.html"

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        if not self.request.session.get("message_sent", False):
            messages.success(self.request, f"Welcome back, {user.username}!")
            self.request.session["message_sent"] = True
        if user.is_superuser:
            return redirect("admin:index")
        elif user.profile.is_expert:
            return redirect("view_mentor_profile", username=user.username)
        else:
            return redirect("view_profile", username=user.username)

    def form_invalid(self, form):
        messages.error(
            self.request, "Login failed. Please check your username and password."
        )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    """A view that handles the logout."""

    template_name = "account/logout.html"
    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            if not self.request.session.get("message_sent", False):
                messages.success(request, "You have been logged out successfully.")
                self.request.session["message_sent"] = True
            logout(request)
            return HttpResponseRedirect(self.get_next_page())
        return self.render_to_response(self.get_context_data())

    def get_next_page(self):
        return str(self.next_page)


def get_user_profile(username):
    """A view that handles the get user profile."""
    return get_object_or_404(Profile, user__username=username)


@login_required
def view_profile(request, username=None):
    """A view that handles the view profile."""
    if username:
        profile = get_object_or_404(Profile, user__username=username)
        is_own_profile = request.user.username == username
    else:
        profile = request.user.profile
        is_own_profile = True

    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
        "has_profile_picture": bool(profile.profile_picture),
    }

    template = (
        "masteryhub/view_mentor_profile.html"
        if profile.is_expert
        else "masteryhub/view_mentee_profile.html"
    )
    return render(request, template, context)


def view_mentor_profile(request, username):
    """A view that handles the view mentor pofile."""
    profile = get_object_or_404(Profile, user__username=username, is_expert=True)
    is_own_profile = (
        request.user.username == username if request.user.is_authenticated else False
    )
    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
    }
    return render(request, "masteryhub/view_mentor_profile.html", context)


@login_required
def edit_profile(request):
    """A view that handles the edit profile."""
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("view_profile", username=profile.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "masteryhub/edit_profile.html", {"form": form})


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
            messages.success(
                request, "Your mentor application has been submitted successfully."
            )
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
    return render(
        request, "masteryhub/search_mentors.html", {"mentors": mentors, "query": query}
    )


@login_required
def request_mentorship(request, mentor_id):
    """A view that handles the mentorship request."""
    mentor_user = get_object_or_404(User, id=mentor_id)
    mentor_profile = get_object_or_404(Profile, user=mentor_user)
    mentee_profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        mentorship, created = Mentorship.objects.get_or_create(
            mentor=mentor_profile, mentee=mentee_profile, status="pending"
        )
        message = (
            f"Mentorship request sent to {mentor_user.username}"
            if created
            else f"You already have a pending request with {mentor_user.username}"
        )
        messages.success(request, message)
        return redirect("view_mentor_profile", username=mentor_user.username)

    return render(
        request, "masteryhub/request_mentorship.html", {"mentor": mentor_user}
    )


@login_required
def manage_mentorship_requests(request):
    """A view that handles the mentroship request management."""
    mentor_profile = get_object_or_404(Profile, user=request.user)
    pending_requests = Mentorship.objects.filter(
        mentor=mentor_profile, status="pending"
    )
    return render(
        request,
        "masteryhub/manage_mentorship_requests.html",
        {"pending_requests": pending_requests},
    )


def list_mentors(request):
    """A view that handles the mentor list."""
    query = request.GET.get('q')
    if query:
        mentors = Profile.objects.filter(is_expert=True).filter(
            Q(user__username__icontains=query) |
            Q(mentorship_areas__icontains=query)
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
        return render(request, "masteryhub/matching_results.html", {"matches": matches})
    else:
        return redirect("login")


@login_required
def expert_dashboard(request):
    """A view that handles the expert dashboard."""
    expert_profile = Profile.objects.get(user=request.user)
    participants = Profile.objects.filter(
        mentorship_areas__icontains=expert_profile.mentorship_areas
    )
    feedbacks = Feedback.objects.filter(mentor=expert_profile)
    sessions = Session.objects.filter(host=expert_profile)

    labels = []
    data = []
    for session in sessions:
        labels.append(session.date.strftime("%B %Y"))
        data.append(1)

    context = {
        "username": request.user.username,
        "participants": participants,
        "feedbacks": feedbacks,
        "sessions": sessions,
        "labels": labels,
        "data": data,
    }
    return render(request, "masteryhub/expert_dashboard.html", context)


@login_required
def mentee_dashboard(request):
    """A view that handles the mentee dashboard."""
    mentee_profile = Profile.objects.get(user=request.user)
    feedbacks = Feedback.objects.filter(mentee=mentee_profile)
    sessions = Session.objects.filter(participants=mentee_profile)

    labels = []
    data = []

    session_counts = (
        sessions.values("date__month")
        .annotate(count=Count("id"))
        .order_by("date__month")
    )

    for entry in session_counts:
        month_name = entry["date__month"]
        labels.append(f"{month_name:02d}")
        data.append(entry["count"])

    skills = mentee_profile.skills.split(",") if mentee_profile.skills else []
    goals = mentee_profile.goals.split(",") if mentee_profile.goals else []

    payments = Payment.objects.filter(user=mentee_profile)
    grand_total = payments.aggregate(Sum("amount"))["amount__sum"] or 0.00

    context = {
        "username": request.user.username,
        "mentee_profile": mentee_profile,
        "feedbacks": feedbacks,
        "skills": skills,
        "goals": goals,
        "labels": labels,
        "data": data,
        "sessions": sessions,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "grand_total": grand_total,
    }
    return render(request, "masteryhub/mentee_dashboard.html", context)


@login_required
def my_mentorships(request):
    """A view that handles my mentorship."""
    user_profile = request.user.profile
    mentorships_as_mentor = Mentorship.objects.filter(mentor=user_profile)
    mentorships_as_mentee = Mentorship.objects.filter(mentee=user_profile)
    context = {
        "mentorships_as_mentor": mentorships_as_mentor,
        "mentorships_as_mentee": mentorships_as_mentee,
    }
    return render(request, "masteryhub/my_mentorships.html", context)


@login_required
def accept_mentorship(request, mentorship_id):
    """A view that handles the accept mentorship."""
    mentorship = get_object_or_404(
        Mentorship, id=mentorship_id, mentor=request.user.profile
    )
    mentorship.status = "accepted"
    mentorship.start_date = timezone.now().date()
    mentorship.save()
    messages.success(
        request, f"Mentorship with {mentorship.mentee.user.username} accepted"
    )
    return redirect("manage_mentorship_requests")


@login_required
def reject_mentorship(request, mentorship_id):
    """A view that handles the reject mentorship."""
    mentorship = get_object_or_404(
        Mentorship, id=mentorship_id, mentor=request.user.profile
    )
    mentorship.status = "rejected"
    mentorship.save()
    messages.success(
        request, f"Mentorship with {mentorship.mentee.user.username} rejected"
    )
    return redirect("manage_mentorship_requests")


def session_list(request):
    """A view that renders the list of sessions with optional filtering."""
    query = request.GET.get("q")
    selected_category = request.GET.get("category")

    sessions = Session.objects.filter(status="scheduled")

    if query:
        sessions = sessions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

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


@login_required
def view_session(request, session_id):
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
            session = form.save(commit=False)
            session.host = request.user
            session.price = form.cleaned_data["price"]
            session.save()
            messages.success(request, "Session created successfully.")
            return redirect("view_session", session_id=session.id)
    else:
        form = SessionForm()
    return render(request, "masteryhub/create_session.html", {"form": form})


@login_required
def edit_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, host=request.user)
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
    session = get_object_or_404(Session, id=session_id, host=request.user)
    if request.method == "POST":
        session.delete()
        messages.success(request, "Session deleted successfully.")
        return redirect("session_list")
    return render(request, "masteryhub/delete_session.html", {"session": session})


@login_required
def create_feedback(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == "POST":
        feedback_content = request.POST.get("feedback")
        Feedback.objects.create(
            session=session, user=request.user, content=feedback_content
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect("view_session", session_id=session_id)
    return render(request, "masteryhub/create_feedback.html", {"session": session})


def forum_posts(request):
    posts = Forum.objects.all()
    return render(request, "masteryhub/forum_posts.html", {"posts": posts})


@login_required
def forum_list(request):
    """A view that handles the forum list."""
    categories = Category.objects.all()
    posts = Forum.objects.filter(parent_post=None)
    return render(
        request,
        "masteryhub/forum_list.html",
        {"categories": categories, "posts": posts},
    )


@login_required
def create_forum_post(request):
    """A view that handles the create forum post."""
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Forum post created successfully.")
            return redirect("forum_posts")
    else:
        form = ForumPostForm()
    return render(request, "masteryhub/create_forum_post.html", {"form": form})


@login_required
@login_required
def view_forum_post(request, post_id):
    """A view that handles the view forum post."""
    post = get_object_or_404(Forum, id=post_id)
    comments = post.comments.all()
    return render(
        request, "masteryhub/view_forum_post.html", {"post": post, "comments": comments}
    )


@login_required
def reply_forum_post(request, post_id):
    """A view that handles the reply forum post."""
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
    return render(
        request,
        "masteryhub/reply_forum_post.html",
        {"form": form, "parent_post": parent_post},
    )


@login_required
def edit_forum_post(request, post_id):
    """A view that handles the edit forum post."""
    post = get_object_or_404(Forum, id=post_id, author=request.user)
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
    """A view that handles the delete forum post."""
    post = get_object_or_404(Forum, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Forum post deleted successfully.")
        return redirect("forum_posts")
    return render(request, "masteryhub/delete_forum_post.html", {"post": post})


@login_required
def book_session(request, session_id):
    """A view that handles the session booking."""
    session = get_object_or_404(Session, id=session_id)
    user_profile = request.user.profile

    if session.is_full():
        messages.error(request, "This session is already full.")
    elif user_profile in session.participants.all():
        messages.warning(request, "You are already booked for this session.")
    else:
        try:
            price_in_cents = int(session.price * 100)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(session.price * 100),
                            "product_data": {
                                "name": session.title,
                                "description": session.description,
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("payment_success"))
                + f"?session_id={{CHECKOUT_SESSION_ID}}&django_session_id={session.id}",
                cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
                client_reference_id=str(session.id),
                customer_email=request.user.email,
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(
                request, "Unable to process booking. Please try again later."
            )
            return redirect("session_list")

    return redirect("session_list")


def pricing(request):
    """A view that handles pricing."""
    return render(request, "masteryhub/pricing.html")


def mentor_rules(request):
    """A view that handles the mentor rules."""
    return render(request, "masteryhub/mentor_rules.html")


def report_concern(request):
    """A view that handles the report concern."""
    if request.method == "POST":
        form = ConcernReportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your concern has been reported. We will review it shortly."
            )
            return redirect("home")
    else:
        form = ConcernReportForm()

    return render(request, "masteryhub/report_concern.html", {"form": form})


def mentor_help(request):
    return render(request, "masteryhub/mentor_help.html")


@login_required
def add_to_cart(request, session_id):
    """A view that adds a session to the user's cart."""
    if request.method == "POST":
        session = get_object_or_404(Session, id=session_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, session=session)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        total = sum(
            item.session.price * item.quantity for item in cart.cartitem_set.all()
        )
        messages.success(request, f"Added {session.title} to your cart.")
        return JsonResponse({"success": True, "total": float(total)})
    messages.error(request, "Failed to add session to cart.")
    return JsonResponse({"success": False})


@login_required
def view_cart(request):
    """A view that renders the user's cart."""
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, "masteryhub/cart.html", {"cart": cart})


@login_required
def checkout(request):
    """A view that handles the checkout process."""
    cart = get_object_or_404(Cart, user=request.user)
    grand_total = sum(
        item.session.price * item.quantity for item in cart.cartitem_set.all()
    )

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            street_address1 = form.cleaned_data["address"]
            street_address2 = form.cleaned_data.get("address2", "")
            county = form.cleaned_data.get("county", "")
            town_or_city = form.cleaned_data["city"]
            postcode = form.cleaned_data.get("postcode", "")
            country = form.cleaned_data["country"]
            phone_number = request.POST.get("phone_number", "")

            order = Order(
                user=request.user,
                order_number="ORD" + str(int(grand_total * 1000)),
                full_name=full_name,
                street_address1=street_address1,
                street_address2=street_address2,
                county=county,
                town_or_city=town_or_city,
                postcode=postcode,
                country=country,
                phone_number=phone_number,
                order_total=grand_total,
                delivery_cost=0,
                grand_total=grand_total,
            )
            order.save()

            payment = Payment.objects.create(
                user=request.user.profile, amount=grand_total, session=None
            )

            cart.cartitem_set.all().delete()

            messages.success(
                request,
                "Your purchase was successful. A confirmation email has been sent to you.",
            )
            return redirect("checkout_success", order_number=order.order_number)
        else:
            messages.error(
                request,
                "There was an error with your order. Please check your details and try again.",
            )
    else:
        form = OrderForm()
        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency="usd",
            metadata={"integration_check": "accept_a_payment"},
        )
        client_secret = intent.client_secret

    context = {
        "order_form": form,
        "client_secret": client_secret,
        "cart": cart,
        "grand_total": grand_total,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "masteryhub/checkout.html", context)


@login_required
def create_checkout_session(request):
    """A view that creates a Stripe Checkout session."""
    cart = get_object_or_404(Cart, user=request.user)
    line_items = []

    for item in cart.cartitem_set.all():
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.session.title,
                    },
                    "unit_amount": int(item.session.price * 100),
                },
                "quantity": item.quantity,
            }
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri("/masteryhub/checkout_success/"),
            cancel_url=request.build_absolute_uri("/masteryhub/payment_cancel/"),
        )
    except stripe.error.InvalidRequestError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"id": checkout_session.id})


@login_required
def payment_cancel(request):
    """A view that handles the payment cancellation."""
    return render(request, "masteryhub/payment_cancel.html")


def complete_purchase(request):
    """A view that handles the purhase complete."""
    return render(request, "masteryhub/purchase_complete.html")


@require_POST
def cache_checkout_data(request):
    try:
        client_secret = request.POST.get("client_secret")
        if not client_secret:
            raise ValueError("Missing client_secret")

        pid = client_secret.split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "cart": json.dumps(request.session.get("cart", {})),
                "save_info": request.POST.get("save_info"),
                "username": request.user.username,
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Error modifying PaymentIntent: {e}")
        messages.error(
            request,
            "Sorry, your payment cannot be processed right now. Please try again later.",
        )
        return HttpResponse(content=str(e), status=400)


def checkout_view(request):
    cart = get_cart(request)
    total = int(cart.total * 100)

    payment_intent = stripe.PaymentIntent.create(
        amount=total,
        currency="usd",
    )

    return render(
        request,
        "masteryhub/checkout.html",
        {
            "client_secret": payment_intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "cart": cart,
            "grand_total": cart.total,
        },
    )


@login_required
def checkout_success(request, order_number):
    """Handle successful checkouts."""
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        "order": order,
        "from_profile": False,
    }
    return render(request, "masteryhub/checkout_success.html", context)


@require_POST
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")


@require_POST
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect("view_cart")


@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, f"Removed {cart_item.session.title} from your cart.")
    return redirect("view_cart")
