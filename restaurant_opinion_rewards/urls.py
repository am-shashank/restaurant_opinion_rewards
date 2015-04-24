from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib import admin

from app.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'restaurant_opinion_rewards.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^manage/', include(admin.site.urls)),
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^signup/$', TemplateView.as_view(template_name="signup.html")),
    
    # methods
    url(r'^signup_user', signup),
    url(r'^search', search_clicked),
    url(r'^home', home),
    url(r'^refer',send_referral),
    url(r'^logout',logout),
    url(r'^checkin', checkin),
    url(r'^', login),

]
