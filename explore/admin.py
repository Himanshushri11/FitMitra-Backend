from django.contrib import admin
from .models import Gym, GymImage, GymReview, Event, Challenge, Article, Trainer, UserEvent, UserChallenge

class GymImageInline(admin.TabularInline):
    model = GymImage
    extra = 1

class GymReviewInline(admin.TabularInline):
    model = GymReview
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'price_range_min', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city', 'address')
    inlines = [GymImageInline, GymReviewInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'status', 'participants_count')
    list_filter = ('status', 'start_time')
    search_fields = ('title',)

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_days', 'difficulty', 'start_date')
    list_filter = ('difficulty',)

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience_years')

admin.site.register(Article)
admin.site.register(UserEvent)
admin.site.register(UserChallenge)
