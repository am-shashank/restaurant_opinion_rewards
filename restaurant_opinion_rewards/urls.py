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
    url(r'^checkin', TemplateView.as_view(template_name="checkin.html")),
    
    # methods
    url(r'^signup_user', signup),
    url(r'^home', home),
    url(r'^refer',send_referral),
    url(r'^logout',logout),
    url(r'^', login),

]
