from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('follow/',
         views.follow_index,
         name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'),
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path('create/',
         views.Post_create.as_view(),
         name='post_create'),
    path('group/<slug:slug>/',
         views.Group_posts.as_view(),
         name='group_posts'),
    path('profile/<str:username>/',
         views.Profile.as_view(),
         name='profile'),
    path('posts/<int:post_id>/',
         views.Post_detail.as_view(),
         name='post_detail'),
    path('', views.Index.as_view(), name='index'),
]
