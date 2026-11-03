from django.contrib import admin
from .models import (
    Category,
    Entrepreneur,
    TimelineMilestone,
    DistilledLesson,
    Video,
    SavedVideo,
    ContactMessage
)

# Custom branding for VentureVault Admin
admin.site.site_header = "VentureVault Administration"
admin.site.site_title = "VentureVault Admin Portal"
admin.site.index_title = "Entrepreneur Video Directory Management"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

class VideoInline(admin.StackedInline):
    model = Video
    extra = 0
    fields = ('title', 'category', 'video_url', 'thumbnail', 'duration', 'is_published', 'featured', 'trending', 'key_takeaways', 'description')
    show_change_link = True

class TimelineMilestoneInline(admin.StackedInline):
    model = TimelineMilestone
    extra = 1
    fields = ('order', 'year_or_date', 'title', 'subtitle', 'description', 'source')

class DistilledLessonInline(admin.TabularInline):
    model = DistilledLesson
    extra = 1
    fields = ('order', 'is_quote', 'quote_or_lesson', 'source')

@admin.register(Entrepreneur)
class EntrepreneurAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'role', 'industry', 'location', 'founded_year', 'is_published', 'featured', 'created_at')
    list_filter = ('is_published', 'industry', 'featured', 'founded_year', 'created_at')
    search_fields = ('name', 'company_name', 'role', 'industry', 'biography', 'location', 'founding_location', 'headquarters')
    prepopulated_fields = {'slug': ('name', 'company_name')}
    list_editable = ('is_published', 'featured')
    inlines = [VideoInline, TimelineMilestoneInline, DistilledLessonInline]
    actions = ['publish_selected', 'unpublish_selected']
    list_per_page = 20

    @admin.action(description="Publish selected entrepreneur stories (make visible publicly)")
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Successfully published {count} entrepreneur story/stories.")

    @admin.action(description="Unpublish selected entrepreneur stories (set as draft / hidden)")
    def unpublish_selected(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"Successfully unpublished {count} entrepreneur story/stories (now drafts).")

@admin.register(TimelineMilestone)
class TimelineMilestoneAdmin(admin.ModelAdmin):
    list_display = ('entrepreneur', 'year_or_date', 'title', 'source', 'order')
    list_filter = ('entrepreneur', 'year_or_date')
    search_fields = ('title', 'subtitle', 'description', 'source', 'entrepreneur__name')
    list_per_page = 25

@admin.register(DistilledLesson)
class DistilledLessonAdmin(admin.ModelAdmin):
    list_display = ('entrepreneur', 'is_quote', 'quote_or_lesson', 'source', 'order')
    list_filter = ('is_quote', 'entrepreneur')
    search_fields = ('quote_or_lesson', 'source', 'entrepreneur__name')
    list_per_page = 25

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'entrepreneur', 'category', 'duration', 'views', 'is_published', 'featured', 'trending', 'created_at')
    list_filter = ('is_published', 'category', 'featured', 'trending', 'created_at')
    search_fields = ('title', 'description', 'entrepreneur__name', 'entrepreneur__company_name')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'featured', 'trending')
    actions = ['publish_selected', 'unpublish_selected']
    list_per_page = 20

    @admin.action(description="Publish selected videos (make visible publicly)")
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Successfully published {count} video(s).")

    @admin.action(description="Unpublish selected videos (set as draft / hidden)")
    def unpublish_selected(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"Successfully unpublished {count} video(s) (now drafts).")

@admin.register(SavedVideo)
class SavedVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'video__title')
    list_per_page = 25

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    list_per_page = 25
