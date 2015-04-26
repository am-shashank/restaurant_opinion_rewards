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
#import qrtools
from random import randint
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
    password = signup_data.get('password')
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



def generate_qr_code(filename, text):
    filename = "database_images/qr_code/bill1.png"
    text = 'restaurant_name:name\nbill_id:id\nitem1:name; quantity:number; price:number\nitem2:name; quantity:number; price:number\ntotal:number\n'
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)

def generate_qr_code_coupon(filename, text):
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)

def generate_survey(request):
    user_id = request.session['username']
    survey_id = request.session['survey_id']
    bill_id = request.session['bill_id']
    restaurant_id = request.session['restaurant_id']
    cursor = connection.cursor()

    # check if survey id already exists in response
    if survey_id is None:
        
        
        #Insert entry into Survey and saving the survey id in session
        cursor.execute("Insert into Survey(user_id) values(%s)",(user_id))
        survey_id = cursor.lastrowid
        request.session['survey_id'] = survey_id

        #Insert entry into Checkin Table
        cursor.execute("Insert into Checkin(survey_id,bill_id,restaurant_id) values(%s,%s,%s)",survey_id,bill_id,restaurant_id)
        
        # send standard 4 questions
        context['questions'] = get_questions("general")
        return render_to_response("survey.html", RequestContext(request, context))

    else:
        survey_data = request.POST
        question_ids = survey_data.get('question_ids').split('#')
        choice_ids = survey_data.get('choice_ids').split('#')
        text = survey_data.get('text')
        question_choice_list = []
        question_choice = ()
        second_page = False
        #Check if the response is for the first time or not.
        if(question_ids[0] == 1):
            second_page = True

        #Iterate over all the responses of the user and store it in response table
        for i in range(len(question_ids)):
            if(choice_ids[i]>0):
                text = "null"
            else:
                text = survey_data.get('text')                
            question_choice = (question_ids[i],choice_ids[i])
            question_choice_list.append(question_choice)
            insert_into_response(choice_ids[i],question_ids[i],survey_id,text)
        print "Data stored in Response table"

        #Generate dyanamic Questions only if this is after the first page.        
        if(second_page):
            #Check the lowest ratings he gave and ask questions about that
            question_choice_list.sort(key=lambda x: x[1])
            if(question_choice_list[0][1] == 5):
                #User is satisfied. So ask restaurant based questions.
                context['questions'] = get_questions("restaurant")            
                return render_to_response("survey.html", RequestContext(request, context))
            else:
                if(question_choice_list[0][1] < 5):
                    cursor.execute('select category from Question where id = %s',(question_choice_list[0][0]))
                    row = cursor.fetchone()
                    category = row[3]
                    context['questions'] = get_final_questions(bill_id,restaurant_id,category,user_id)
                    return render_to_response("survey.html", RequestContext(request, context))


def get_questions(category):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    #Get the questions based on category
    cursor.execute('select * from Question where category = %s',(category))
    questions = {}
    for row in cursor.fetchall():
        question_id = row[0]
        question_text = row[1]
        questions[question_id] = {}
        questions[question_id]['text'] = question_text
        #Get the choices for the corresponding Question Id from the Has_Choice table
        cursor1.execute('select c.id,c.text from Has_Choice h, Choice c where h.choice_id = c.id and h.question_id = %s',(question_id))
        for choices in cursor1.fetchall():
            choice_id = choices[0]
            choice_text = choices[1]
            questions[question_id][choice_id] = choice_text

    questions["is_survey"] = "True"
    return questions

def insert_into_response(choice_id,question_id,survey_id,text):
    cursor = connection.cursor()
    cursor.execute("Insert into Response(choice_id,question_id,survey_id,text) values(%s,%s,%s,%s)",(choice_id,question_id,survey_id,text))

def get_final_questions(bill_id,restaurant_id,category,user_id):
    cursor = connection.cursor()
    cursor1 = connection.cursor()

    cursor.execute('select * from Question q where q.category = %s and q.id not in \
            (select question_id from Response r,Survey s where r.survey_id = s.id \
            and s.user_id = %s and s.restaurant_id = %s',(category,user_id,restaurant_id))
    cnt = 0
    for row in cursor.fetchall():
        #Fetch two questions from the list and then break
        if cnt == 2:
                break
        question_id = row[0]
        question_text = row[1]
        questions[question_id] = {}
        questions[question_id]['text'] = question_text
        #Get the choices for the corresponding Question Id from the Has_Choice table
        cursor1.execute('select c.id,c.text from Has_Choice h, Choice c where h.choice_id = c.id and h.question_id = %s',(question_id))
        for choices in cursor1.fetchall():
                choice_id = choices[0]
                choice_text = choices[1]
                questions[question_id][choice_id] = choice_text
        cnt+=1


    #Ask a question from the Bill
    cursor.execute('select item_name from Has_Bill where bill_id = %s and restaurant_id = %s \
        ORDER BY RAND()  LIMIT 1')
    first_entry = cursor.fetchone()
    item_name = first_entry[0]
    inserted_id = insert_into_question(item_name)
    questions[inserted_id] = {}
    cursor.execute('select * from Choice where id>0 and id<6')
    for choices in cursor.fetchall():
        choice_id = choices[0]
        choice_text = choices[1]
        questions[inserted_id][choice_id] = choice_text

    #Ask a generic question for Other comments
    other_comments = "Enter any additional comments:"
    other_comments_id = 0
    questions[other_comments_id]['text'] = other_comments

    #Set the flag to indicate that no more surveys
    questions["is_survey"] = "False"
    return questions

def insert_into_question(item_name):
    text = "How would you rate " + item_name + "?"
    cursor = connection.cursor()
    cursor.execute("Insert into Question(text) values(%s)",(text))
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