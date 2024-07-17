from django.contrib import admin
from .models import Session, Profile, Category, Mentorship, Review, Payment, Forum

# Register your models here.

admin.site.register(Session)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Mentorship)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Forum)
