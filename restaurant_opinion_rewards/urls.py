from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib import admin

from app.views import *
from business.views import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'restaurant_opinion_rewards.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^manage/', include(admin.site.urls)),
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^signup', TemplateView.as_view(template_name="signup.html")),
    url(r'^index', TemplateView.as_view(template_name="login.html")),

    # user side methods
    url(r'^insert', insert),
    url(r'^create_user', signup),
    url(r'^search', search_clicked),
    url(r'^generate_event', generate_event),
    url(r'^home', home),
    url(r'^survey', survey),
    url(r'^refer',send_referral),
    url(r'^logout',logout),
    url(r'^checkin', checkin),
    url(r'^get_reviews', get_reviews),
    url(r'^display', display),
    url(r'^delete_coupon', delete_coupon),
    url(r'^generate_survey', generate_survey),
    url(r'^generate_coupon', generate_coupon),

    # business side methods
    url(r'^business/create_bill', create_bill_render),
    url(r'^business/generate_bill', generate_bill),
    url(r'^business/get_overall_averages', get_overall_averages),
    url(r'^business/get_no_checkins', get_no_checkins),
    url(r'^business/get_favourite_items', get_favourite_items),
    url(r'^business/home', TemplateView.as_view(template_name="business_login.html")),
    url(r'^business/user_likings',user_likings),

    # default
    url(r'^', login),
]
