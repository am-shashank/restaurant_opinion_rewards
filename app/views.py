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
from django.conf import settings
import time
import os
import hashlib
import redis

#import qrtools
from random import randint
import pyqrcode

from django.http import JsonResponse

cursor = connection.cursor()

def get_md5hash(str):
    return hashlib.md5(str).hexdigest()

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


@csrf_exempt
def insert(request):
    return HttpResponseRedirect('/signup')

@csrf_exempt
def display(request):
    return HttpResponseRedirect('/index')

@csrf_exempt
@require_POST
def signup(request):
    print "Signup function is getting executed"

    signup_data = request.POST
    id = signup_data.get('username')
    first_name = signup_data.get('firstname')
    last_name = signup_data.get('lastname')
    dob = signup_data.get('dob')
    email = signup_data.get('email')
    password = get_md5hash(signup_data.get('password'))
    # facebook_id = signup_data.get('facebook_id')
    telephone = signup_data.get('phone')
    message = ""

    credit = 0
    print "It's a new account"
    # create new User and save it.
    cursor = connection.cursor()
    try:
        cursor.execute('insert into User(id, first_name, last_name, dob, email, credit, telephone) values(%s, %s, %s, %s, %s, %s, %s)', (id, first_name, last_name, dob, email, credit, telephone))
    except:
        return HttpResponse("Error inserting to database. Please Try again!")
    try:
        cursor.execute('insert into Login(user_id, password) values(%s, %s)', (id, password))
    except:
        return HttpResponse("Username already exists. Please try with a different username!")
   
    print "Created User"

    # create login credentials and save it

    # save friend list to database

    # TO DO: send welcome email
    message = "Successfully created account."
    return HttpResponse(message)


def get_nearby_restaurants(latitude, longitude):
    # print "from get_nearby_restaurants: " + latitude
    startlat = float(latitude)
    startlng = float(longitude)
    cursor = connection.cursor()
    cursor.execute('SELECT id,name,full_address,stars, latitude, longitude, image_path, SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance from Restaurant HAVING distance < 25 ORDER BY distance LIMIT 48',(startlat,startlng))
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
        d['image_path'] = row[6]
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
    password = get_md5hash(login_data.get('password'))
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
        request.session['users_latitude'] = login_data.get('latitude')
        request.session['users_longitude'] = login_data.get('longitude')
    # set the entire session object
    request.session['context'] = context
    # test_query(request)

    # fetch all the coupons associated with the current user
    coupons = {}
    i = 1
    cursor = connection.cursor()
    cursor.execute("select Coupons.id, Coupons.restaurant_id, Restaurant.name, Coupons.deal, Coupons.image_path from Coupons, Restaurant where user_id = '"+request.session['username']+"' and Restaurant.id = Coupons.restaurant_id;")
    
    results = cursor.fetchall()

    for coupon in results:

        coupons[str(i)] = {}
        # check for expires or filter them using query
        d = {}
        d['id'] = coupon[0]
        # coupon.restaurant_id is actually restuarant object
        if coupon[1] is not None:
            d['restaurant_id'] = coupon[1]
        try:
            if coupon[1] is not None:
                d['restaurant_name'] = coupon[2]
        except Restaurant.DoesNotExist:
            message = "restaurant does not exist"
            return HttpResponse(message)
        d['deal'] = coupon[3]
        d['image_path'] = coupon[4]
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
        you check into the restaurant. Both of your credit points will be increased."
    except:
        return HttpResponse('Database insertion failed.')

    try:
        send_msg(message, phone_number)
    except:
        message = "Message Deliver Failed!"
        return HttpResponse(message)
    message = "Referral sent Successfully!"
    return HttpResponse(message)


@csrf_exempt
def generate_event(request):
    event_data = request.POST
    restaurant_id = ""
    username = ""
    phone_numbers = event_data.get('phone_numbers')
    event_message = event_data.get('event_message')
    if 'restaurant_id' in request.session:
        restaurant_id = request.session['restaurant_id']
        username = request.session['username']
    else:
        return HttpResponse("Failed to generate event")

    cursor = connection.cursor()
    cursor.execute('select name from Restaurant where id=\''+restaurant_id+'\'')
    row = cursor.fetchone()
    restaurant_name = row[0]
    print restaurant_name
    cursor.execute('select first_name from User where id=\''+username+'\'')
    row = cursor.fetchone()
    display_name = row[0]

    print display_name

    collect_phone_numbers = phone_numbers.split(";")
    message = display_name+" has invited to his event at "+restaurant_name+"\nMessage : "+event_message
    for phone_number in collect_phone_numbers:
        print phone_number
        send_msg(message, phone_number)

    return HttpResponse("Event Update : Invited members successfully")
    


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
    if 'username' in request.session:
        print "Logging out ...." + request.session['username']
    else:
        print "Username not in session"
    try:
        del request.session['username']
        del request.session['context']
    except KeyError:
        pass

    request.session.flush()
    print request.session
    # return HttpResponse('Success')
    return HttpResponseRedirect('/')


@csrf_exempt
def search_clicked(request):
    print "Inside search_clicked"
    search_data = request.POST
    print "latitude: " + str(search_data.get('latitude'))
    print "longitue: " + str(search_data.get('longitude'))
    if 'context' in request.session:
        context = request.session['context']
    else:
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
    context['users_latitude'] = request.session['users_latitude']
    context['users_longitude'] = request.session['users_longitude']
    context['restaurant'] = restaurant
    reviews = Review.objects.filter(restaurant_id=restaurant_id)
    i = 1
    for review in reviews:
        context['review' + str(i)] = review
        i += 1
    request.session['restaurant_id'] = restaurant.id
    return render_to_response("checkin.html", RequestContext(request, context))

@csrf_exempt
def survey(request):
    if 'username' not in request.session:
        print "session not set"
        return HttpResponseRedirect('/')
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
    bd.printObj()

    cursor = connection.cursor()
    # get restaurant_id from restaurant name
    cursor.execute(
        'select id from Restaurant where name=\''+bd.restaurant_name+'\'')
    row = cursor.fetchone()
    print row[0]
    if row is not None:
        restaurant_id = row[0]
    else:
        return HttpResponse('Oops sorry. Restaurant was not found. Try later')
    try:
        query = 'insert into Bill(id, restaurant_id, amount, time) values('+bd.bill_id+',\''+restaurant_id+'\','+ bd.total+','+bd.time+');'
        print query
        cursor.execute(query)
        print "Query executed"
    except:
        return HttpResponse('Something wrong with the bill. use the correct QR Code')
    for i in range(len(bd.item_name)):
        try:
            query = 'insert into Has_Bill(item_name, restaurant_id, bill_id, quantity) values(\''+bd.item_name[i]+'\',\''+restaurant_id+'\','+ bd.bill_id+','+bd.item_quantity[i]+');'
            print query
            cursor.execute(query)
        except:
            return HttpResponse('Something wrong with the bill. use the correct QR Code')

    # call generate survey
    request.session['bill_id'] = bd.bill_id
    request.session['restaurant_id'] = restaurant_id
    bill_id = bd.bill_id
    user_id = request.session['username']

    #Insert entry into Survey and saving the survey id in session
    query = "Insert into Survey(user_id,restaurant_id) values('" + user_id + "','" + restaurant_id + "')"
    print query
    cursor.execute(query)
    survey_id = cursor.lastrowid
    request.session['survey_id'] = survey_id
    
    query = "Insert into Checkin(survey_id,bill_id,restaurant_id) values('" + str(survey_id) + "','" + str(bill_id) +  "',\
            '" + str(restaurant_id)  +  "')"
    #Insert entry into Checkin Table
    try:
        cursor.execute(query)
    except:
        return HttpResponse("Something went wrong while Checkin.")

    question_ids = {}
    question_ids['question_1'] = 1
    question_ids['question_2'] = 2
    question_ids['question_3'] = 3
    question_ids['question_4'] = 4
    request.session['question_ids'] = question_ids

    question_option_ids = {}
    for i in range(1,5):
        question_option_ids['question_' + str(i)] = {}
        for j in range(1,6):
            question_option_ids['question_' + str(i)]['option_' + str(j)] = j

    request.session['question_option_ids'] = question_option_ids

    #Setting the context and sending it in response for displaying credit
    user = User.objects.get(id=user_id)
    context = {
        "first_name": user.first_name,
        "credit": user.credit
    }
    return render_to_response('survey.html', RequestContext(request, request.session['context']))


def save_uploaded_file(f, filename):
    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)
    # destination = open(filename, 'wb+')
    with open(filename, 'a') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

# class which parses the qrcode string and sets the bill data
class BillData:

    def __init__(self, qrcode_text):
        self.item_name = []
        self.item_quantity = []
        self.item_price = []
        for line in qrcode_text.splitlines():
            line = line.strip()
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
    restaurant_id = request.GET.get("id")
    response_object = {}
    # restaurant_id = 'mVHrayjG3uZ_RLHkLj-AMg'
    r=redis.Redis(host='pub-redis-13102.us-east-1-4.1.ec2.garantiadata.com', port=13102,password='brogrammer')
    reviews = 'empty'
    reviews = r.lpop(restaurant_id)
    print "rest id : "+restaurant_id
    if reviews is None:
        cursor = connection.cursor()
        cursor.execute('select text from Review where restaurant_id=\''+restaurant_id + '\'')
    # print "REVIEWS FOR CURRENT RESTAURANT" + cursor.fetchall()
    # return JsonResponse(response_object)
        results = cursor.fetchall()
        i = 1
        for row in results:
            response_object['review_' + str(i)] = row[0]
            print "In get_reviews: "+row[0]
            r.lpush(restaurant_id, row[0])
            i = i + 1
    else:
        print "Obtaining reviews from redis cache"
        #print reviews[0]
        collect_reviews = []
        
        while reviews is not None:
            collect_reviews.append(reviews)
            reviews = r.lpop(restaurant_id)
                
        i = 1
        for review in collect_reviews:
            #print "In cache : "+review
            response_object['review_' + str(i)] = review
            r.lpush(restaurant_id, review)
            i = i+1
        
    return JsonResponse(response_object)


@csrf_exempt
@require_POST
def generate_coupon(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('/')
    coupon_data = request.POST
    points = int(coupon_data.get('points'))
    user_id = request.session['username']
    deal = 'Get discount for '+str(points)+' points in any restaurant'
    image_path = '/static/images/user_coupons/coupon'+str(randint(1,1000))+'.jpeg'
    generate_qr_code_coupon('./app'+image_path, str(points))
    context = request.session['context']
    if int(context['credit'])<points:
        return HttpResponseRedirect("/")
    cursor = connection.cursor()
    credit = int(context['credit']) - points

    try:
        cursor.execute('insert into Coupons(user_id, deal, image_path) values(%s, %s, %s)', (user_id, deal, image_path))
        cursor.execute("update User set credit='"+str(credit)+"' where id='"+request.session['username']+"';")
        cursor.execute("select * from Coupons where user_id = '"+request.session['username']+"' and image_path = '"+image_path+"';")
    except:
        return HttpResponse("Failed to generate coupon")

    if 'coupons' not in context:
        coupons = {}
    else:
        coupons = context['coupons']
    results = cursor.fetchall()
    d= {}
    for row in results:
        d['id'] = row[0]
        d['restaurant_id'] =row[2]
        d['deal'] = row[3]
        d['image_path'] = row[5]
    
    coupons[str(len(coupons)+1)] = d
    context['credit'] = str(credit)
    context['coupons'] = coupons
    request.session['context'] = context
    return HttpResponseRedirect("/home")


def generate_qr_code_coupon(filename, text):
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)


@csrf_exempt
def generate_survey(request):
    if 'username' not in request.session:
        print "session not set"
        return HttpResponseRedirect('/')
    print "In generate survey"
    survey_id = request.session['survey_id']
    bill_id = request.session['bill_id']
    restaurant_id = request.session['restaurant_id']
    user_id = request.session['username']
    cursor = connection.cursor()

    # check if survey id already exists in response
    if survey_id is None:
        # send standard 4 questions
        context['questions'] = get_questions("general")
        return render_to_response("survey.html", RequestContext(request, context))

    else:
        question_ids_session = request.session['question_ids']
        question_option_ids_session = request.session['question_option_ids']
        print "question_ids " 
        print question_ids_session
        print "question_option_ids "
        print question_option_ids_session
        survey_data = request.POST
        print survey_data
        question_choice_list = []
        for key in survey_data:
            value = survey_data[key]    
            question_choice = (question_ids_session[key],question_option_ids_session[key][value])
            question_choice_list.append(question_choice)

        print question_choice_list
        #question_ids = survey_data.get('question_ids').split('#')
        #choice_ids = survey_data.get('choice_ids').split('#')
        
        text = survey_data.get('text')
        #second_page = False
        #Check if the response is for the first time or not.
        #if(question_ids[0] == 1):
        #    second_page = True
        second_page = False
        #Iterate over all the responses of the user and store it in response table
        print str(len(question_choice_list))
        for i in range(len(question_choice_list)):
            if(question_choice_list[i][1]>0):
                text = "null"
            else:
                text = survey_data.get('text')
            questionid = question_choice_list[i][0]
            if(questionid<5):
                second_page = True
            choiceid = question_choice_list[i][1]             
            insert_into_response(choiceid,questionid,survey_id,text)
        print "Data stored in Response table"
        
        #Generate dyanamic Questions only if this is after the first page.        
        if(second_page):
            #Check the lowest ratings he gave and ask questions about that
            question_choice_list.sort(key=lambda x: x[1],reverse = True)
            if(question_choice_list[0][1] == 1):
                #User is satisfied. So ask restaurant based questions.
                questions = get_questions("restaurant",request)
                print questions            
                return JsonResponse(questions)
            else:
                    cursor.execute('select text from Question where id = ' + str(question_choice_list[0][0]))
                    row = cursor.fetchone()
                    category = row[0]
                    print category
                    questions = get_final_questions(bill_id,restaurant_id,category,user_id,request)
                    print questions
                    return JsonResponse(questions)
        else:
            questions = {}
            questions['is_survey'] = "False"
            query = 'update User set credit = credit + 5 where id  = \'' + user_id + '\''
            print query
            cursor.execute(query)
            return JsonResponse(questions)

def get_questions(category,request):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    #Get the questions based on category
    query = 'select * from Question where category = \'' + category + '\''
    print query
    cursor.execute(query)
    request.session['question_ids'] = {}
    request.session['question_option_ids'] = {}
    question_ids_session = {}
    question_option_ids_session = {}

    questions = {}
    i=0
    for row in cursor.fetchall():
        i+=1
        question_id = row[0]
        question_text = row[1]
        questions["question_" + str(i)] = {}
        questions["question_" + str(i)]['question_text'] = question_text
        
        # Save in question_ids_session
        question_ids_session["question_" + str(i)] = question_id

        #Get the choices for the corresponding Question Id from the Has_Choice table
        query = 'select c.id,c.text from Has_Choice h, Choice c where h.choice_id = c.id and h.question_id = \'' + str(question_id) + '\''
        print query
        cursor1.execute(query)
        j=0
        question_option_ids_session['question_' + str(i)] = {}
        for choices in cursor1.fetchall():
            j+=1
            choice_id = choices[0]
            choice_text = choices[1]
            # Save in session the mapping
            question_option_ids_session['question_' + str(i)]['option_' + str(j)] = choice_id
            questions["question_" + str(i)]["option_" + str(j)] = choice_text

    questions["is_survey"] = "True"
    request.session['question_ids'] = question_ids_session
    request.session['question_option_ids'] = question_option_ids_session
    return questions

def insert_into_response(choice_id,question_id,survey_id,text):
    cursor = connection.cursor()
    query = "Insert into Response(choice_id,question_id,survey_id,text) values(\
        '" + str(choice_id) + "','" + str(question_id) + "','" + str(survey_id) + "','" + str(text) + "')"
    print query
    cursor.execute(query)

def get_final_questions(bill_id,restaurant_id,category,user_id,request):
    cursor = connection.cursor()
    cursor1 = connection.cursor()

    query = 'select * from Question q where q.category = \'' + category +'\'and q.id not in \
            (select question_id from Response r,Survey s where r.survey_id = s.id\
            and s.user_id = \''+ str(user_id) + '\'and s.restaurant_id = \''+ str(restaurant_id) + '\')'
    print query
    cursor.execute(query)

    #Resetting the sessions to null
    request.session['question_ids'] = {}
    request.session['question_option_ids'] = {}
    
    # Initialize the dicts
    question_ids_session = {}
    question_option_ids_session = {}
    questions = {}
    i=0


    #Counter to keep track of the number of questions to display
    cnt = 0

    for row in cursor.fetchall():
        print row[0],row[1]
        #Fetch two questions from the list and then break
        if cnt == 2:
                break
        question_id = row[0]
        question_text = row[1]
        i+=1
        #Initialize the dict and set the question text.
        questions["question_" + str(i)] = {}
        questions["question_" + str(i)]['question_text'] = question_text

        # Save in question_ids_session for future mapping.
        question_ids_session["question_" + str(i)] = question_id

        #Get the choices for the corresponding Question Id from the Has_Choice table        
        query = 'select c.id,c.text from Has_Choice h, Choice c where h.choice_id = c.id and h.question_id = \'' + str(question_id) + '\''
        print query
        cursor1.execute(query)
        j=0
        question_option_ids_session['question_' + str(i)] = {}
        for choices in cursor1.fetchall():
            j+=1
            choice_id = choices[0]
            choice_text = choices[1]
            # Save in session the mapping
            question_option_ids_session['question_' + str(i)]['option_' + str(j)] = choice_id
            #Set the object questions which is to be returned.
            questions["question_" + str(i)]["option_" + str(j)] = choice_text
        cnt+=1


    #Ask a question from the Bill
    query = 'select item_name from Has_Bill where bill_id = \'' + str(bill_id)  + '\'and restaurant_id \
    =\'' + restaurant_id  +'\'ORDER BY RAND()  LIMIT 1'
    print query 
    cursor.execute(query)
    first_entry = cursor.fetchone()
    item_name = first_entry[0]
    
    #Get the inserted id from the Question table after inserting.
    inserted_id = insert_into_question(item_name)
    question_text = "How would you rate " + item_name + "?"
    i+=1
    questions["question_" + str(i)] = {}
    questions["question_" + str(i)]['question_text'] = question_text
    # Save in question_ids_session for future mapping.
    question_ids_session["question_" + str(i)] = inserted_id
    question_option_ids_session['question_' + str(i)] = {}
    cursor.execute('select * from Choice where id>0 and id<6')
    j=0
    for choices in cursor.fetchall():
        j+=1
        choice_id = choices[0]
        choice_text = choices[1]
        # Save in session the mapping
        question_option_ids_session['question_' + str(i)]['option_' + str(j)] = choice_id
        #Set the object questions which is to be returned.
        questions["question_" + str(i)]["option_" + str(j)] = choice_text

    #TODO: Ask a generic question for Other comments
    #other_comments = "Enter any additional comments:"
    #other_comments_id = 0
    #questions[other_comments_id]['text'] = other_comments

    request.session['question_ids'] = question_ids_session
    request.session['question_option_ids'] = question_option_ids_session

    #Set the flag to true
    questions["is_survey"] = "True"
    return questions

def insert_into_question(item_name):
    text = "How would you rate " + item_name + "?"
    cursor = connection.cursor()
    one = 1
    category = "dynamic"
    query = 'Insert into Question(text,flag,category) values(\'' + text + '\',\'\
            ' + str(one) + '\',\'' + str(category) + '\')' 
    print query
    cursor.execute(query)
    inserted_id = cursor.lastrowid
    return inserted_id

@csrf_exempt
def delete_coupon(request):
    coupon_data = request.POST
    coupon_id = coupon_data.get('coupon_id')
    print "Coupon Id : "+str(coupon_id)

    try:
        Coupons.objects.filter(id=coupon_id).delete()
        print "deleted Coupon from Database : "+str(coupon_id)
    except:
        print "Error in deleteing coupon :"+str(coupon_id)+ " from Coupons Model."

    if 'context' in request.session:
        context = request.session['context']
    else:
        context = {}

    coupons = {}
    i = 1
    cursor = connection.cursor()
    cursor.execute("select Coupons.id, Coupons.restaurant_id, Restaurant.name, Coupons.deal, Coupons.image_path from Coupons, Restaurant where user_id = '"+request.session['username']+"' and Restaurant.id = Coupons.restaurant_id;")
    
    results = cursor.fetchall()

    for coupon in results:

        coupons[str(i)] = {}
        # check for expires or filter them using query
        d = {}
        d['id'] = coupon[0]
        # coupon.restaurant_id is actually restuarant object
        if coupon[1] is not None:
            d['restaurant_id'] = coupon[1]
        try:
            if coupon[1] is not None:
                d['restaurant_name'] = coupon[2]
        except Restaurant.DoesNotExist:
            message = "restaurant does not exist"
            return HttpResponse(message)
        d['deal'] = coupon[3]
        d['image_path'] = coupon[4]
        coupons[str(i)] = d
        i += 1

    context['coupons'] = coupons
    request.session['context'] = context
    print "Context object after setting coupons"
    print context
    return HttpResponseRedirect('/home')   
