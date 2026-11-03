from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.urls import reverse

from .models import Category, Entrepreneur, Video, SavedVideo, ContactMessage
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    ContactForm,
    UserProfileUpdateForm
)

def _get_user_saved_video_ids(user):
    """
    Helper returning set of video IDs saved by the given authenticated normal user.
    Admins and staff accounts cannot bookmark stories, so an empty set is returned.
    """
    if user.is_authenticated and not (user.is_staff or user.is_superuser):
        return set(SavedVideo.objects.filter(user=user).values_list('video_id', flat=True))
    return set()

def home_view(request):
    """
    Homepage showcasing hero section, curated featured stories,
    trending videos, category domains, founder spotlights, and platform metrics.
    Only published stories and videos are visible.
    """
    featured_videos = Video.objects.select_related('entrepreneur', 'category').filter(
        is_published=True,
        entrepreneur__is_published=True,
        featured=True
    )[:6]
    if not featured_videos.exists():
        featured_videos = Video.objects.select_related('entrepreneur', 'category').filter(
            is_published=True,
            entrepreneur__is_published=True
        )[:6]

    trending_videos = Video.objects.select_related('entrepreneur', 'category').filter(
        is_published=True,
        entrepreneur__is_published=True,
        trending=True
    )[:4]
    if not trending_videos.exists():
        trending_videos = Video.objects.select_related('entrepreneur', 'category').filter(
            is_published=True,
            entrepreneur__is_published=True
        ).order_by('-views')[:4]

    featured_categories = Category.objects.filter(
        videos__is_published=True,
        videos__entrepreneur__is_published=True
    ).annotate(
        video_count=Count('videos', filter=Q(videos__is_published=True, videos__entrepreneur__is_published=True))
    ).order_by('-video_count')[:8]
    if not featured_categories.exists():
        featured_categories = Category.objects.annotate(
            video_count=Count('videos', filter=Q(videos__is_published=True, videos__entrepreneur__is_published=True))
        ).order_by('-video_count')[:8]

    spotlight_entrepreneurs = Entrepreneur.objects.filter(is_published=True, featured=True)[:3]
    if not spotlight_entrepreneurs.exists():
        spotlight_entrepreneurs = Entrepreneur.objects.filter(is_published=True)[:3]

    stats = {
        'total_videos': Video.objects.filter(is_published=True, entrepreneur__is_published=True).count(),
        'total_entrepreneurs': Entrepreneur.objects.filter(is_published=True).count(),
        'total_categories': Category.objects.count(),
    }

    context = {
        'featured_videos': featured_videos,
        'trending_videos': trending_videos,
        'categories': featured_categories,
        'spotlight_entrepreneurs': spotlight_entrepreneurs,
        'stats': stats,
        'saved_video_ids': _get_user_saved_video_ids(request.user),
    }
    return render(request, 'directory/home.html', context)

def explore_view(request):
    """
    Full video directory with keyword search, category filtering,
    sorting options, and responsive pagination.
    Only published videos and entrepreneurs are returned.
    """
    videos_list = Video.objects.select_related('entrepreneur', 'category').filter(
        is_published=True,
        entrepreneur__is_published=True
    )

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        videos_list = videos_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(key_takeaways__icontains=search_query) |
            Q(entrepreneur__name__icontains=search_query) |
            Q(entrepreneur__company_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Category filter
    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        videos_list = videos_list.filter(category__slug=selected_category)

    # Sorting filter
    sort_by = request.GET.get('sort', 'newest').strip()
    if sort_by == 'popular':
        videos_list = videos_list.order_by('-views', '-created_at')
    elif sort_by == 'oldest':
        videos_list = videos_list.order_by('created_at')
    elif sort_by == 'title':
        videos_list = videos_list.order_by('title')
    else:  # newest default
        videos_list = videos_list.order_by('-created_at')

    # Pagination: 6 items per page
    paginator = Paginator(videos_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'total_results': videos_list.count(),
        'saved_video_ids': _get_user_saved_video_ids(request.user),
    }
    return render(request, 'directory/explore.html', context)

def video_detail_view(request, pk):
    """
    Single video view featuring YouTube embed player, founder details,
    structured key takeaways, bookmarking (for normal users), and related stories.
    Authorized admin/staff can preview draft videos. Anonymous/normal users only see published.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        video = get_object_or_404(Video.objects.select_related('entrepreneur', 'category'), pk=pk)
    else:
        video = get_object_or_404(
            Video.objects.select_related('entrepreneur', 'category'),
            pk=pk,
            is_published=True,
            entrepreneur__is_published=True
        )

    # Increment view count
    video.views += 1
    video.save(update_fields=['views'])

    # Related stories: published videos only
    related_videos = Video.objects.select_related('entrepreneur', 'category').filter(
        is_published=True,
        entrepreneur__is_published=True
    ).filter(
        Q(category=video.category) | Q(entrepreneur=video.entrepreneur)
    ).exclude(pk=video.pk).order_by('-views')[:4]

    is_saved = False
    if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
        is_saved = SavedVideo.objects.filter(user=request.user, video=video).exists()

    context = {
        'video': video,
        'takeaways': video.get_takeaways_list(),
        'embed_url': video.get_youtube_embed_url(),
        'youtube_id': video.get_youtube_video_id(),
        'related_videos': related_videos,
        'is_saved': is_saved,
    }
    return render(request, 'directory/video_detail.html', context)

def entrepreneurs_view(request):
    """
    Directory of featured and all entrepreneurs with search and industry filtering.
    Only published entrepreneurs are displayed.
    """
    entrepreneurs_list = Entrepreneur.objects.filter(is_published=True).annotate(
        video_count=Count('videos', filter=Q(videos__is_published=True))
    ).order_by('name')

    search_query = request.GET.get('q', '').strip()
    if search_query:
        entrepreneurs_list = entrepreneurs_list.filter(
            Q(name__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(biography__icontains=search_query)
        )

    selected_industry = request.GET.get('industry', '').strip()
    if selected_industry:
        entrepreneurs_list = entrepreneurs_list.filter(industry__iexact=selected_industry)

    industries = Entrepreneur.objects.filter(is_published=True).values_list('industry', flat=True).distinct()
    industries = sorted([ind for ind in set(industries) if ind])

    paginator = Paginator(entrepreneurs_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'industries': industries,
        'search_query': search_query,
        'selected_industry': selected_industry,
        'total_results': entrepreneurs_list.count(),
    }
    return render(request, 'directory/entrepreneurs.html', context)

def entrepreneur_detail_view(request, pk):
    """
    Entrepreneur profile detail: biography, journey timeline,
    all videos featuring this founder, and aggregated key lessons.
    Authorized admin/staff can preview draft entrepreneurs; public visitors only see published.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        entrepreneur = get_object_or_404(Entrepreneur, pk=pk)
        videos = Video.objects.filter(entrepreneur=entrepreneur).select_related('category')
    else:
        entrepreneur = get_object_or_404(Entrepreneur, pk=pk, is_published=True)
        videos = Video.objects.filter(entrepreneur=entrepreneur, is_published=True).select_related('category')

    # Verified distilled lessons from database with primary source attribution
    db_lessons = list(entrepreneur.distilled_lessons.all().order_by('order', 'id'))
    if db_lessons:
        lessons = [
            {
                'text': l.quote_or_lesson,
                'is_quote': l.is_quote,
                'source': l.source,
            }
            for l in db_lessons
        ]
    else:
        video_lessons = []
        for v in videos:
            video_lessons.extend(v.get_takeaways_list())
        lessons = [{'text': t, 'is_quote': False, 'source': ''} for t in video_lessons[:6]]

    context = {
        'entrepreneur': entrepreneur,
        'videos': videos,
        'lessons': lessons,
        'saved_video_ids': _get_user_saved_video_ids(request.user),
    }
    return render(request, 'directory/entrepreneur_detail.html', context)

def categories_view(request):
    """
    Overview of all business categories and domains with published video counts.
    """
    categories = Category.objects.annotate(
        video_count=Count('videos', filter=Q(videos__is_published=True, videos__entrepreneur__is_published=True))
    ).all().order_by('-video_count')
    context = {
        'categories': categories,
    }
    return render(request, 'directory/categories.html', context)

def category_videos_view(request, slug):
    """
    Video listings filtered by a specific category.
    Only published videos and entrepreneurs are listed.
    """
    category = get_object_or_404(Category, slug=slug)
    videos_list = Video.objects.filter(
        category=category,
        is_published=True,
        entrepreneur__is_published=True
    ).select_related('entrepreneur', 'category')

    sort_by = request.GET.get('sort', 'newest').strip()
    if sort_by == 'popular':
        videos_list = videos_list.order_by('-views')
    elif sort_by == 'oldest':
        videos_list = videos_list.order_by('created_at')
    else:
        videos_list = videos_list.order_by('-created_at')

    paginator = Paginator(videos_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'sort_by': sort_by,
        'total_results': videos_list.count(),
        'saved_video_ids': _get_user_saved_video_ids(request.user),
    }
    return render(request, 'directory/category_videos.html', context)

def search_view(request):
    """
    Multi-model search across published videos, entrepreneurs, and categories.
    """
    query = request.GET.get('q', '').strip()
    videos = []
    entrepreneurs = []
    categories = []

    if query:
        videos = Video.objects.select_related('entrepreneur', 'category').filter(
            is_published=True,
            entrepreneur__is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(key_takeaways__icontains=query) |
            Q(entrepreneur__name__icontains=query) |
            Q(entrepreneur__company_name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

        entrepreneurs = Entrepreneur.objects.filter(
            is_published=True
        ).filter(
            Q(name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(industry__icontains=query) |
            Q(biography__icontains=query)
        ).distinct()

        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    total_count = len(videos) + len(entrepreneurs) + len(categories)

    context = {
        'query': query,
        'videos': videos,
        'entrepreneurs': entrepreneurs,
        'categories': categories,
        'total_count': total_count,
        'saved_video_ids': _get_user_saved_video_ids(request.user),
    }
    return render(request, 'directory/search_results.html', context)

def about_view(request):
    """About VentureVault, mission statement, and educational purpose."""
    stats = {
        'total_videos': Video.objects.filter(is_published=True, entrepreneur__is_published=True).count(),
        'total_entrepreneurs': Entrepreneur.objects.filter(is_published=True).count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'directory/about.html', {'stats': stats})

def contact_view(request):
    """Contact page and message handling."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting VentureVault! Our editorial team has received your message.")
            return redirect('contact')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            initial_data['name'] = full_name if full_name else request.user.username
            initial_data['email'] = request.user.email
        form = ContactForm(initial=initial_data)

    return render(request, 'directory/contact.html', {'form': form})

def register_view(request):
    """User registration view with automatic login on success."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to VentureVault, {user.username}! Your account has been created successfully.")
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'directory/register.html', {'form': form})

def login_view(request):
    """User authentication view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            # Prevent open redirect vulnerability
            if not next_url.startswith('/'):
                next_url = 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'directory/login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logs out the user and redirects to home page."""
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('home')

@login_required
def profile_view(request):
    """
    User dashboard: view/edit personal details and browse saved videos.
    Admins are informed that bookmarks are reserved for reader accounts.
    """
    if request.method == 'POST':
        p_form = UserProfileUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
    else:
        p_form = UserProfileUpdateForm(instance=request.user)

    is_admin = request.user.is_staff or request.user.is_superuser
    if not is_admin:
        saved_videos = SavedVideo.objects.filter(user=request.user).select_related(
            'video__entrepreneur', 'video__category'
        )
    else:
        saved_videos = []

    context = {
        'p_form': p_form,
        'saved_videos': saved_videos,
        'is_admin': is_admin,
    }
    return render(request, 'directory/profile.html', context)

@login_required
@require_POST
def remove_saved_video_view(request, video_id):
    """
    Removes a video from the user's saved list.
    Admins/superusers cannot bookmark stories and are rejected with 403 Forbidden.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Admin and staff accounts cannot manage bookmarks.")

    video = get_object_or_404(Video, pk=video_id)
    SavedVideo.objects.filter(user=request.user, video=video).delete()
    messages.success(request, f"Removed '{video.title}' from your saved videos.")
    next_url = request.POST.get('next') or request.GET.get('next') or 'profile'
    if not next_url.startswith('/'):
        next_url = 'profile'
    return redirect(next_url)

@require_POST
def toggle_save_video(request, video_id):
    """
    AJAX endpoint to toggle saving a video to the user's personal vault.
    - Anonymous visitor: rejected with 401 Unauthorized.
    - Admin / Superuser: rejected with 403 Forbidden (bookmarking is reserved for reader accounts).
    - Normal registered user: toggles saved status.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'unauthenticated',
            'message': 'Please log in to save videos to your vault.',
            'login_url': f"{reverse('login')}?next={request.META.get('HTTP_REFERER', '/')}"
        }, status=401)

    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({
            'status': 'forbidden',
            'message': 'Admin and staff accounts cannot bookmark stories. Content management is handled in the Admin Panel.'
        }, status=403)

    video = get_object_or_404(Video, pk=video_id, is_published=True, entrepreneur__is_published=True)
    saved_item, created = SavedVideo.objects.get_or_create(user=request.user, video=video)

    if not created:
        saved_item.delete()
        is_saved = False
        message = f"Removed '{video.title}' from your vault."
    else:
        is_saved = True
        message = f"Saved '{video.title}' to your vault!"

    total_saved = SavedVideo.objects.filter(user=request.user).count()
    return JsonResponse({
        'status': 'success',
        'is_saved': is_saved,
        'message': message,
        'saved_count': total_saved
    })
