from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
import datetime
from twilio.rest import TwilioRestClient
from app.models import *
import collections
import json
from django.db import connection
from django.db import transaction
from django.conf import settings
import time
import os
import qrtools
import pyqrcode
from django.http import JsonResponse

cursor = connection.cursor()


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
            message = "Account already exists. Please login here. <a href=" // ">Login</a>"
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
    cursor.execute(
        'SELECT id,name,full_address,stars, latitude, longitude, SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance from Restaurant HAVING distance < 25 ORDER BY distance LIMIT 48', (startlat, startlng))
    results = cursor.fetchall()
    # 4 indicates number of columns in the grid on home.html
    total_required_results = len(results) - len(results) % 4
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
    if request.method == 'GET':
        # Redirect to home page if the session is set
        if 'username' in request.session:
            print request.session
            return HttpResponseRedirect('/home/')
        elif 'context' in request.session:
            print request.session['context']
            return render_to_response("login.html", RequestContext(request, request.session['context']))
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
        # return render_to_response("/signin", RequestContext(request,
        # context))
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
        context["nearby_restaurants"] = get_nearby_restaurants(
            login_data.get('latitude'), login_data.get('longitude'))
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

    referral_data = request.POST
    phone_number = referral_data.get('phone')
    restaurant_id = referral_data.get('restaurant_id')
    print "Received referral for " + restaurant_id + " from " + request.session['username']
    # check if the friend has already been referred
    print phone_number
    cursor = connection.cursor()
    cursor.execute('SELECT id from User where telephone=\'' + phone_number+'\'')
    # cursor.fetchone()
    for row in cursor.fetchall():
        referee_id = row[0]
    if cursor.rowcount == 0:
        print "friend not on resoprew"
        return HttpResponse("Your friend is not on Restaurant opinion Rewards. You can only refer to "
                            +
                            "friends who are using our platform. Please invite your friend to use Restaurant"
                            + "opinion rewards.")

    cursor.execute(
        'select * from Refers where restaurant_id=%s and referee_telephone=%s', (restaurant_id, phone_number))
    if cursor.rowcount != 0:
        print "friend already referred"
        return HttpResponse("Your friend has already been refereed. Please refer another friend.")

    # insert to Refers table
    try:
        cursor.execute("insert into Refers(referer_id, referee_id, restaurant_id, referee_telephone) values(%s, %s \
        ,%s , %s)", (request.session['username'], referee_id, restaurant_id, phone_number))
        message = "Your friend has been sent a message and a coupon which can be redeemed at the restaurant. Once \
        he checks into the restaurant. Your credit points will be increased."
    except:
        return HttpResponse('Database insertion failed.')

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
    ACCOUNT_SID = "AC61c18e7de16e85b26a27c182862bccde"
    AUTH_TOKEN = "71fd7355a691839a0ddc94029945880e"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    # Information corresponds to the phone number associated with the account that is used to send sms etc.
    # Then a message is created which is routed to the client_number through
    # twilio number of the account.

    client.messages.create(
        body=intro_msg,
        to=client_number,
        from_="+16788203937",
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
    print "Logging out ...." + request.session['username']
    try:
        del request.session['username']
        del request.session['context']
    except KeyError:
        pass

    request.session.flush()
    print request.session
    return HttpResponse('Success')


@csrf_exempt
def search_clicked(request):
    search_data = request.POST
    context = {}
    if 'latitude' in search_data and 'longitude' in search_data:
        context["nearby_restaurants"] = get_nearby_restaurants(
            search_data.get('latitude'), search_data.get('longitude'))
    # set the session object
    request.session['context'] = context
    return HttpResponseRedirect('/login')

# gets the restaurant id and sets the context dictionary which is used in
# checkin.html

@csrf_exempt
def checkin(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('/')
    restaurant_id = request.GET.get('id')

    # fetch data about restaurant and set the context object
    # id, name, full_address, latitude, longitude, stars, image_path, reviews
    restaurant = Restaurant.objects.get(id=restaurant_id)
    # context dictionary which will be used in
    context = {}
    context['restaurant'] = restaurant
    reviews = Review.objects.filter(restaurant_id=restaurant_id)
    i = 1
    for review in reviews:
        context['review' + str(i)] = review
        i += 1
    return render_to_response("checkin.html", RequestContext(request, context))

@csrf_exempt
@require_POST
def survey(request):
    checkin_data = request.POST
    restaurant_id = checkin_data.get('survey_restaurant_id')
    # save the qr code file using the current timestamp as the filename
    filename = settings.BASE_DIR + 'app/database_images/' + str(time.time())
    save_uploaded_file(request.FILES['qrcode_image'], filename)
    # save_uploaded_file(checkin_data['qrcode_image'], filename)
    # decode the file
    qr = qrtools.QR()
    qr.decode(filename)

    # parse the decoded qr code string into a data structure
    bd = BillData(qr.data)

    cursor = connection.cursor()

    # get restaurant_id from restaurant name
    cursor.execute(
        'select id from Restaurant where name=\''+bd.restaurant_name+'\'')
    row = cursor.fetchone()
    if row is not None:
        restaurant_id = row[0]
    else:
        return HttpResponse('Oops sorry. Restaurant was not found. Try later')
    try:
        query = 'insert into Bill(id, restaurant_id, amount, time) values('+bd.bill_id+',\''+restaurant_id+'\','+ bd.total+','+bd.time+');'
        cursor.execute(query)
    except:
        return HttpResponse('Something wrong with the bill. use the correct QR Code')
    for i in range(len(bd.item_name)):
        try:
            query = 'insert into Has_Bill(item_name, restaurant_id, bill_id, quantity) values(\''+bd.item_name[i]+'\',\''+restaurant_id+'\','+ bd.bill_id+','+bd.item_quantity[i]+');'
            cursor.execute(query)
        except:
            return HttpResponse('Something wrong with the bill. use the correct QR Code')

    # call generate survey
    request.session['bill_id'] = bd.bill_id
    request.session['restaurant_id'] = restaurant_id
    return HttpResponseRedirect('/generate_survey')


def save_uploaded_file(f, filename):
    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)
    # destination = open(filename, 'wb+')
    with open(filename, 'a') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()


def generate_survey(request):
    survey_data = request.POST
    survey_id = survey_data.get('survey_id')
    # check if survey id already exists in response
    cursor = connection.cursor()
    cursor.execute('select * from Response where survey_id = %s', (survey_id))
    # if cursor.rowcount == 0: # send standard 4 questions

    # else: # check the lowest ratings he gave and ask questions about that


# class which parses the qrcode string and sets the bill data
class BillData:

    def __init__(self, qrcode_text):
        self.item_name = []
        self.item_quantity = []
        self.item_price = []
        for line in qrcode_text.splitlines():
            key_value = line.split(':', 2)
            if len(key_value) >= 2:
                if key_value[0] == 'restaurant_name':
                    self.restaurant_name = key_value[1].strip()
                elif key_value[0] == 'bill_id':
                    self.bill_id = key_value[1].strip()
                elif key_value[0].startswith('item') is True:
                    for item_detail in line.split(';'):
                        detail = item_detail.split(':')
                        if detail[0].strip().startswith('item'):
                            self.item_name.append(detail[1].strip())
                        elif detail[0].strip() == 'quantity':
                            self.item_quantity.append(detail[1].strip())
                        elif detail[0].strip() == 'price':
                            self.item_price.append(detail[1].strip())
                elif key_value[0] == 'total':
                    self.total = key_value[1].strip()
                elif key_value[0] == 'time':
                    self.time = key_value[1].strip()

    def printObj(self):
        print "Restaurant Name:" + self.restaurant_name
        print "Bill ID: " + self.bill_id
        print "Total: " + self.total
        for i in range(len(self.item_name)):
            print "item_name: " + self.item_name[i] + " quantity: " + self.item_quantity[i] + " price:" + self.item_price[i]
        return

def get_reviews(request):
    response_object={"review":"good"}
    print "IN get_reviews"
    restaurant_id = request.GET.get("id")
    # restaurant_id = 'mVHrayjG3uZ_RLHkLj-AMg'
    cursor = connection.cursor()
    cursor.execute('select text from Review where restaurant_id=\''+restaurant_id + '\'')
    # print "REVIEWS FOR CURRENT RESTAURANT" + cursor.fetchall()
    # return JsonResponse(response_object)
    results = cursor.fetchall()
    response_object = {}
    i = 1
    for row in results:
        response_object['review_' + str(i)] = row[0]
        i = i + 1
    return JsonResponse(response_object)

def generate_qr_code(filename, text):
    filename = "database_images/qr_code/bill1.png"
    text = 'restaurant_name:name\nbill_id:id\nitem1:name; quantity:number; price:number\nitem2:name; quantity:number; price:number\ntotal:number\n'
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)