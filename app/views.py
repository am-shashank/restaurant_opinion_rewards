from django.shortcuts import render
from django.http import HttpResponse
import datetime
from app.models import *

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
    facebook_id = signup_data.get('facebook_id')
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

def login(request):
    login_data = request.POST
    username = login_data.get('username')
    password = login_data.get('password')
    try:
        user = Login.objects.get(username=username)
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
    return HttpResponse(message)
