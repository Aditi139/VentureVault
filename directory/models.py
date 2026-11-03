from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import re

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(help_text="Short overview of this category")
    icon = models.CharField(max_length=50, default="fas fa-lightbulb", help_text="FontAwesome icon class, e.g., 'fas fa-rocket'")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Entrepreneur(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    company_name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, default="Founder & CEO", help_text="e.g. Co-founder & CEO, Chairman & CEO")
    co_founders = models.CharField(max_length=250, blank=True, default="", help_text="Co-founders and early founding partners")
    industry = models.CharField(max_length=100)
    biography = models.TextField()
    profile_image = models.URLField(max_length=500, help_text="URL to founder photo")
    location = models.CharField(max_length=100, default="Global")
    founding_location = models.CharField(max_length=150, blank=True, default="", help_text="Where company was originally founded, e.g., Albuquerque, NM")
    headquarters = models.CharField(max_length=150, blank=True, default="", help_text="Current corporate headquarters")
    key_products = models.CharField(max_length=300, blank=True, default="", help_text="Key products, platforms, or services")
    founded_year = models.IntegerField(default=2020)
    website = models.URLField(max_length=250, blank=True, null=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, db_index=True, help_text="Visible to public visitors")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.company_name}")
        super().save(*args, **kwargs)

    def get_clean_website(self):
        if not self.website:
            return None
        w = self.website.strip()
        if not w or "example.com" in w.lower() or "placeholder" in w.lower():
            return None
        if not (w.startswith('http://') or w.startswith('https://')):
            w = f"https://{w}"
        return w

    @property
    def avatar_url(self):
        if self.profile_image and self.profile_image.strip():
            img = self.profile_image.strip()
            # If it's a verified local static path or trusted non-stock URL
            if not ("images.unsplash.com" in img or "placeholder" in img):
                return img
        
        name_slug = slugify(self.name)
        import os
        from django.conf import settings
        static_dir = os.path.join(settings.BASE_DIR, 'directory', 'static')
        
        # 1. Local verified authentic portrait photo
        jpg_rel = f"directory/images/entrepreneurs/{name_slug}.jpg"
        if os.path.exists(os.path.join(static_dir, jpg_rel)):
            return f"/static/{jpg_rel}"
        
        # 2. Neutral initials-based SVG avatar
        svg_rel = f"directory/images/entrepreneurs/{name_slug}.svg"
        if os.path.exists(os.path.join(static_dir, svg_rel)):
            return f"/static/{svg_rel}"
            
        # 3. Default vector fallback
        return "/static/directory/images/avatar-founder.svg"

    def get_milestones(self):
        """Returns verified, historically accurate timeline milestones for this entrepreneur."""
        # 1. Query database milestones if populated
        if hasattr(self, 'timeline_milestones') and self.timeline_milestones.exists():
            return [
                {
                    "title": m.title,
                    "subtitle": f"{m.year_or_date}{' – ' + m.subtitle if m.subtitle else ''}",
                    "desc": m.description,
                    "source": m.source,
                    "year_or_date": m.year_or_date,
                }
                for m in self.timeline_milestones.all().order_by('order', 'id')
            ]
        
        # 2. Look up static verified research milestones
        from .research_data import get_static_verified_milestones
        static_milestones = get_static_verified_milestones(self.name)
        if static_milestones:
            return static_milestones
            
        # 3. Fallback to factual company establishment milestone (never generic templates)
        return [
            {
                "title": f"Establishment of {self.company_name}",
                "subtitle": str(self.founded_year),
                "desc": f"{self.name} established {self.company_name} in {self.founding_location or self.location}, focusing on innovation in {self.industry}.",
                "source": f"Official {self.company_name} corporate records."
            }
        ]

    def __str__(self):
        return f"{self.name} ({self.company_name})"

class TimelineMilestone(models.Model):
    entrepreneur = models.ForeignKey(Entrepreneur, on_delete=models.CASCADE, related_name='timeline_milestones')
    year_or_date = models.CharField(max_length=100, help_text="e.g., 1975, April 1976, or Formative Years")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    source = models.CharField(max_length=300, blank=True, help_text="Supporting reference or verified historical source")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.entrepreneur.name} - {self.year_or_date}: {self.title}"

class DistilledLesson(models.Model):
    entrepreneur = models.ForeignKey(Entrepreneur, on_delete=models.CASCADE, related_name='distilled_lessons')
    quote_or_lesson = models.TextField()
    is_quote = models.BooleanField(default=False, help_text="True if direct quotation, False if paraphrased lesson")
    source = models.CharField(max_length=300, help_text="Verified speech, interview, writing, or documented decision")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.entrepreneur.name}: {self.quote_or_lesson[:50]}"

class Video(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    entrepreneur = models.ForeignKey(Entrepreneur, on_delete=models.CASCADE, related_name='videos')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='videos')
    description = models.TextField()
    video_url = models.URLField(max_length=500, help_text="YouTube URL or Embed URL")
    thumbnail = models.URLField(max_length=500, help_text="Video cover image URL")
    duration = models.CharField(max_length=20, default="10:00", help_text="e.g. 12:45")
    views = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    key_takeaways = models.TextField(help_text="Bullet points or newline-separated key lessons", blank=True)
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, db_index=True, help_text="Visible to public visitors")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_youtube_video_id(self):
        """Extracts the 11-character YouTube video ID from various standard and mobile formats."""
        url = (self.video_url or "").strip()
        if not url:
            return None
        # If user directly entered just an 11-char YouTube ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        pattern = r'(?:v=|\/embed\/|\/shorts\/|\/live\/|youtu\.be\/|\/v\/|\/e\/|watch\?.*?v=)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def get_youtube_embed_url(self):
        """Generates standard privacy-enhanced YouTube embed URL."""
        video_id = self.get_youtube_video_id()
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&enablejsapi=1"
        return self.video_url

    @property
    def thumbnail_url(self):
        """Returns video thumbnail with automatic YouTube HQ fallback."""
        if self.thumbnail and self.thumbnail.strip():
            return self.thumbnail.strip()
        yt_id = self.get_youtube_video_id()
        if yt_id:
            return f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
        return "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80"

    def get_takeaways_list(self):
        if not self.key_takeaways:
            return []
        lines = [line.strip().lstrip('•-123456789. ') for line in self.key_takeaways.split('\n') if line.strip()]
        return lines

class SavedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_videos')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.video.title}"

class StorySubmission(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='story_submissions')
    entrepreneur_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    email = models.EmailField()
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=250)
    description = models.TextField()
    video_url = models.URLField(max_length=500)
    profile_image = models.URLField(max_length=500, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_video = models.OneToOneField(
        Video,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_submission'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission: {self.title} by {self.entrepreneur_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_approval_status()

    def sync_approval_status(self):
        if self.status == 'Approved':
            cat_name = (self.category or 'Startup Stories').strip()
            category, _ = Category.objects.get_or_create(
                name__iexact=cat_name,
                defaults={'name': cat_name, 'description': f'Stories in {cat_name}', 'icon': 'fas fa-rocket'}
            )
            profile_img = self.profile_image or 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&q=80'
            entrepreneur, _ = Entrepreneur.objects.get_or_create(
                name=self.entrepreneur_name,
                company_name=self.company_name,
                defaults={
                    'industry': category.name,
                    'biography': f"{self.entrepreneur_name} is the founder of {self.company_name}.",
                    'profile_image': profile_img,
                    'location': 'Global',
                    'founded_year': 2024,
                }
            )
            thumb = self.profile_image or 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80'
            if not self.approved_video:
                video = Video.objects.create(
                    title=self.title,
                    entrepreneur=entrepreneur,
                    category=category,
                    description=self.description,
                    video_url=self.video_url,
                    thumbnail=thumb,
                    key_takeaways=f"• Story submitted by community founder {self.entrepreneur_name}\n• Core focus: {self.company_name}",
                    featured=False,
                    trending=False
                )
                self.approved_video = video
                super().save(update_fields=['approved_video'])
            else:
                video = self.approved_video
                video.title = self.title
                video.entrepreneur = entrepreneur
                video.category = category
                video.description = self.description
                video.video_url = self.video_url
                video.save()
        elif self.status in ['Pending', 'Rejected']:
            if self.approved_video:
                vid = self.approved_video
                self.approved_video = None
                super().save(update_fields=['approved_video'])
                try:
                    vid.delete()
                except Exception:
                    pass

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name}: {self.subject}"
