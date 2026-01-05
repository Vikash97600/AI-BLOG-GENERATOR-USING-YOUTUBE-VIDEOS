from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login', user_login, name='login'),
    path('signup', user_signup, name='signup'),
    path('logout', user_logout, name='logout'),
    path('forgot_password', forgot_password, name='forgot_password'),
    path('change_password', change_password, name='change_password'),
    path('generate-blog', generate_blog, name='generate-blog'),
    path('blog-list', blog_list, name='blog-list'),
    path('blog-details/<int:pk>', blog_details, name='blog-details'),
    path('download_blog_qr/<int:pk>', download_blog_qr, name='download_blog_qr'),
    path('translate', translate_blog, name='translate_blog'),
    path('delete-blog/<int:pk>/', delete_blog, name='delete_blog'),
    path("recently_deleted_blogs/", recently_deleted_blogs, name="recently_deleted_blogs"),
    path("restore-blog/<int:pk>/",restore_blog, name="restore_blog"),
    path("permanent-delete-blogs/", permanent_delete_blogs, name="permanent_delete_blogs"),
    path('download-pdf/<int:pk>/', generate_pdf, name='generate_pdf'),
    path('share/', share_on_whatsapp, name='share_on_whatsapp'),
]