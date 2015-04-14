from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from app.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'restaurant_opinion_rewards.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^signup/$', TemplateView.as_view(template_name="signup.html")),
    url(r'^home', TemplateView.as_view(template_name="home.html")),
    # url(r'^', TemplateView.as_view(template_name="login.html")),
    url(r'^', login),


    # methods
    url(r'^signup_user', signup),
    # url(r'^login_user', login),
    url(r'^test/$', get_table_list)

]
