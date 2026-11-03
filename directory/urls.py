from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('explore/', views.explore_view, name='explore'),
    path('video/<int:pk>/', views.video_detail_view, name='video_detail'),
    path('video/<int:video_id>/toggle-save/', views.toggle_save_video, name='toggle_save_video'),
    path('saved-video/<int:video_id>/remove/', views.remove_saved_video_view, name='remove_saved_video'),
    path('entrepreneurs/', views.entrepreneurs_view, name='entrepreneurs'),
    path('entrepreneur/<int:pk>/', views.entrepreneur_detail_view, name='entrepreneur_detail'),
    path('categories/', views.categories_view, name='categories'),
    path('category/<slug:slug>/', views.category_videos_view, name='category_videos'),
    path('search/', views.search_view, name='search'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
