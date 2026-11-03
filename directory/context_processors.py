from .models import Category, SavedVideo

def global_context(request):
    """
    Supplies global navigation data to all templates:
    all active categories and authenticated normal user's saved video count.
    Admins/superusers do not bookmark, so their count is always 0.
    """
    try:
        categories = Category.objects.all().order_by('name')
        saved_count = 0
        if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
            saved_count = SavedVideo.objects.filter(user=request.user).count()
        return {
            'all_categories': categories,
            'global_saved_count': saved_count,
        }
    except Exception:
        return {
            'all_categories': [],
            'global_saved_count': 0,
        }
