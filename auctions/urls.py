from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', views.create_listing, name='create_listing'),
    path('close_listing/<str:listing_id>', views.close_listing, name='close_listing'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('listings/<str:listing_id>', views.listing, name='listing'),
    path('place_bid/<str:listing_id>', views.bid, name='bid'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('watchlist/<str:listing_id>', views.watchlist, name='watchlist'),
    path('comment/<str:listing_id>', views.comment, name='comment')
]
