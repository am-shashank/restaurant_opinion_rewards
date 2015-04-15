from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
import datetime
from twilio.rest import TwilioRestClient 
from app.models import *
import collections
import json
from django.db import connection

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
    #print "from get_nearby_restaurants: " + latitude
    startlat = float(latitude)
    startlng = float(longitude)
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
    login_data = request.POST
    print "latitude: " + str(login_data.get('latitude'))
    print "longitue: " + str(login_data.get('longitude'))
    if request.method == 'GET':
        # Redirect to home page if the session is set
        if 'username' in request.session:
            print request.session
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response("login.html")

    # verify login credentials
    
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
        context["nearby_restaurants"] = get_nearby_restaurants(login_data.get('latitude'), login_data.get('longitude'))
    # set the entire session object
    print "Context"
    print context
    request.session['context'] = context
    return render_to_response("home.html", RequestContext(request, context))


@csrf_exempt
def send_referral(request):
    # get request
    if request.method == 'GET':
        # Redirect to home page if the session is set
        if 'username' in request.session:
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response("login.html")

    referral_data = request.POST
    phone_number = referral_data.get('phone')
    username = request.session['username']
    # insert hotel information into the request object when user clicks on card
    # get hotel information from the request  object and create a message
    message = "Hey Dhondu, Khana khayega... Dhondu hotel pe chalo paise bachaoo - " + username

    try:
        user = Login.objects.get(user_id=username)
    except User.DoesNotExist:
        message = "Account doesn't exist. Please create one here. <a href=\"/signup\">Login</a>"
        # return HttpResponseRedirect('/signup')
        return HttpResponse(message)
    user = User.objects.get(id=username)
    context = {
        "first_name": user.first_name,
        "credit": user.credit
    }

    try:
        send_msg(message, phone_number)
    except:
        message = "Message Deliver Failed!"
        # return HttpResponseRedirect('/signup')
        return HttpResponse(message)
    message = "Referral sent Successfully!"
    # return HttpResponseRedirect('/signup')
    return HttpResponse(message)

# send_msg function takes in message as string and phone_number as string
def send_msg(intro_msg, client_number):
        # The registered twilio account is then verified, based on the given parameters and the information necessary to send the sms with the given account is obtained.
    # Twilio Integration
    # put your own credentials here
    ACCOUNT_SID = "ACe142168c1b1c86c9933529838dadd1ec"
    AUTH_TOKEN = "7c14a72a5766def39513501be12abd92"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    # Information corresponds to the phone number associated with the account that is used to send sms etc.
    # Then a message is created which is routed to the client_number through twilio number of the account.
        
    message = client.messages.create(
        body=intro_msg,
        to=client_number,
        from_="+17707286369",
    )

def home(request):
    # check if user is logged in
    if 'username' not in request.session:
        print "session not set"
        return HttpResponseRedirect('/')
    else:
        print "session already set"
        return render_to_response("home.html", RequestContext(request, request.session['context']))

@csrf_exempt
def logout(request):
    print "Logging out ...."+ request.session['username']
    try:
        del request.session['username']
        del request.session['context']
    except KeyError:
        pass

    request.session.flush()
    print request.session
    
    return HttpResponse('Success')


def test_coupon_query(request):
    context = request.session['context']
    coupons_list = []
    for coupon in Coupons.objects.filter(user_id=request.session['username']):
        d = collections.OrderedDict()
        d['id'] = coupon.id
        d['restaurant_id'] = coupon.restaurant_id
    j = json.dumps(coupons_list)

