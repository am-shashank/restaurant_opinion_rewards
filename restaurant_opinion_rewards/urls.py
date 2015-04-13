from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from app.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'restaurant_opinion_rewards.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/$', include(admin.site.urls)),
    url(r'^test/$', get_table_list),
    url(r'^signup/$', TemplateView.as_view(template_name="signup.html")),
    url(r'^signup_user', signup)
]
