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
    # print "from get_nearby_restaurants: " + latitude
    startlat = float(latitude)
    startlng = float(longitude)
    cursor = connection.cursor()
    cursor.execute('SELECT id,name,full_address,stars, latitude, longitude, SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance from Restaurant HAVING distance < 25 ORDER BY distance LIMIT 48',(startlat,startlng))
    results = cursor.fetchall()

    # 4 indicates number of columns in the grid on home.html
    total_required_results = len(results) / 4
    # 2 level dictionary indices
    i = 0
    j = 0
    objects = {}
    for row in results:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        d['full_address'] = row[2]
        d['stars'] = row[3]
        d['latitude'] = row[4]
        d['longitude'] = row[5]
        if i % 4 == 0:
            j += 1
            objects[str(j)] = {}
        objects[str(j)][str(i % 4)] = d
        i += 1
        if i == total_required_results:
            break
    return objects

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
    except Login.DoesNotExist:
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
    request.session['context'] = context
    # test_query(request)

    # fetch all the coupons associated with the current user
    coupons = {}
    i = 1
    for coupon in Coupons.objects.filter(user_id=request.session['username']):
        coupons[str(i)] = {}
        # check for expires or filter them using query
        d = {}
        d['id'] = coupon.id
        # coupon.restaurant_id is actually restuarant object
        d['restaurant_id'] = coupon.restaurant_id.id
        try:
            d['restaurant_name'] = coupon.restaurant_id.name
        except Restaurant.DoesNotExist:
            message = "restaurant does not exist"
            return HttpResponse(message)
        d['deal'] = coupon.deal
        d['image_path'] = coupon.image_path
        coupons[str(i)] = d
        i += 1

    context['coupons'] = coupons
    request.session['context'] = context
    print "Context object after setting coupons"
    print context
    return HttpResponseRedirect('/home')
    # return render_to_response("home.html", RequestContext(request, context))


@csrf_exempt
def send_referral(request):
    # redirect to login page if session has not been set
    if 'username' not in request.session:
        return render_to_response('login.html')

    referral_data = request.GET
    phone_number = referral_data.get('phone')
    restaurant_id = referral_data.get('restaurant_id')

    # check if the friend has already been referred
    try:
        Refers.objects.get(restaurant_id=restaurant_id, referee_telephone=phone_number)
    except Refers.DoesNotExist:
        return HttpResponse("Your friend has already been refereed. Please refer another friend.")

    try:
        user = User.objects.filter(telephone=phone_number)
    except User.DoesNotExist:
        return HttpResponse("Your friend is not on Restaurant opinion Rewards. You can only refer to \
            to friends who are using our platform. Please invite your friend to use Restaurant \
            opinion rewards.")

    # insert to Refers table
    refers = Refers(
                    referer_id=request.session['username'],
                    referee_id=user.id,
                    restaurant_id=restaurant_id,
                    referee_telephone=phone_number
                    )
    refers.save()

    message = "Your friend has been sent a message and a coupon which can be redeemed at the restaurant. Once \
    he checks into the restaurant. Your credit points will be increased."

    try:
        send_msg(message, phone_number)
    except:
        message = "Message Deliver Failed!"
        return HttpResponse(message)
    message = "Referral sent Successfully!"
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
    
    client.messages.create(
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