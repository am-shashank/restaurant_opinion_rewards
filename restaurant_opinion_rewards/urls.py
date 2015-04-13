from django.conf.urls import include, url
from django.contrib import admin

from app.views import (
    current_datetime)

urlpatterns = [
    # Examples:
    # url(r'^$', 'restaurant_opinion_rewards.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/', current_datetime),
]
