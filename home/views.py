from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import HttpResponse
from .forms import ContactForm

# Create your views here.


def index(request):
    """
    A view to return the index page for the home app
    """
    return render(request, "home/index.html")


def about(request):
    return render(request, "home/about.html")


def contact(request):
    return render(request, "home/contact.html")


def contact_view(request):
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

            return redirect("contact")
    else:
        form = ContactForm()

    message_sent = request.session.pop("message_sent", False)

    return render(
        request, "home/contact.html", {"form": form, "message_sent": message_sent}
    )
