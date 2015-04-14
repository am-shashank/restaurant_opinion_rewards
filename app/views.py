from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
import datetime
from app.models import *
import collections
import json

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def get_table_list(request):
    results = User.objects.all()
    # html = "<html><body>"
    html = ""
    for p in results:
        html += p.first_name
    # html += "</body></html>"
    return HttpResponse(html)


def signup(request):
    signup_data = request.POST
    id = signup_data.get('id')
    first_name = signup_data.get('first_name')
    last_name = signup_data.get('last_name')
    dob = signup_data.get('dob')
    email = signup_data.get('email')
    password = signup_data.get('password')
    # facebook_id = signup_data.get('facebook_id')
    phone = signup_data.get('phone')
    users = User.objects.all()
    message = ""
    for user in users:
        if user.id == id:
            message = "Account already exists. Please login here. <a href="//">Login</a>"
            return HttpResponse(message)

    # create new User and save it.
    new_user = User(
        id=id,
        first_name=first_name,
        last_name=last_name,
        dob=dob,
        email=email,
        credit=0
    )
    new_user.save()

    # create login credentials and save it
    '''new_login = Login(
        user=id,
        facebook_id=facebook_id,
        password=password)
    new_login.save()'''

    # save friend list to database

    # TO DO: send welcome email
    request.session['userid'] = id
    message = "Successfully created account."
    return HttpResponse(message)


def get_nearby_restaurants(latitude, longitude):
    startlat = float('latitude')
    startlng = float('longitude')
    cursor = connection.cursor()
    cursor.execute('SELECT id,name,full_address,stars, latitude, longitude, SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance from Restaurant HAVING distance < 25 ORDER BY distance LIMIT 50',(startlat,startlng))
    results = cursor.fetchall()
    print results
    objects_list = []
    for row in results:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['name'] = row[1]
        d['full_address'] = row[2]
        d['stars'] = row[3]
        d['latitude'] = row[4]
        d['longitude'] = row[5]
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

@csrf_exempt
def login(request):
    # get request
    if request.method == 'GET':
        # Redirect to home page if the session is set
        if 'username' in request.session:
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response("login.html")

    # verify login credentials
    login_data = request.POST
    username = login_data.get('username')
    password = login_data.get('password')
    try:
        user = Login.objects.get(user_id=username)
    except User.DoesNotExist:
        message = "Account doesn't exist. Please create one here. <a href=\"/signup\">Login</a>"
        # return HttpResponseRedirect('/signup')
        return HttpResponse(message)
    if user.password != password:
        message = "Wrong password. Please try again. <a href=\"/\">Login</a>"
        # return render_to_response("/signin", RequestContext(request, context))
        return HttpResponse(message)
    else:
        request.session['username'] = username
        message = "You have logged in Successfully"
    user = User.objects.get(id=username)

    context = {
        "first_name": user.first_name,
        "credit": user.credit
    }
    # get nearby restaurants if latitude and longitude are not null
    if 'latitude' in login_data and 'longitude' in login_data:
        context["nearby_restaurants"] = get_nearby_restaurants()
    print context
    return render_to_response("home.html", RequestContext(request, context))
