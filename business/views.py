from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
from django.db import connection
from datetime import datetime
from django.http import JsonResponse
import pyqrcode
# Create your views here.

@csrf_exempt
@require_POST
def generate_bill(request):
    bill_data = request.POST
    restaurant_name = bill_data.get('restaurant_name')
    bill_id = str(bill_data.get('bill_id'))
    item1 = bill_data.get('item1')
    quantity1 = str(bill_data.get('quantity1'))
    price1 = str(bill_data.get('price1'))
    item2 = bill_data.get('item2')
    quantity2 = str(bill_data.get('quantity2'))
    price2 = str(bill_data.get('price2'))
    total = str(bill_data.get('total'))
    filename = "business/database_images/qr_code/"+restaurant_name + '_' + bill_id + '.png'
    text = 'restaurant_name:'+restaurant_name+'\n\
    bill_id:'+bill_id+'\n\
    item1:'+item1+'; quantity:'+quantity1+'; price:'+price1+'\n\
    item2:'+item2+'; quantity:'+quantity2+'; price:'+price2+'\n\
    total:'+total+'\n\
    time:'+str(datetime.now().time().hour)
    print text
    qr = pyqrcode.create(text)
    qr.png(filename, scale=6)
    return HttpResponse('QR Code succcessfully created')

def create_bill_render(request):
    print "dsfklsd"
    cursor = connection.cursor()
    i = 1
    items = {}
    fetch_items_sitar_india = 'select name from Item where restaurant_id=\'testID\';'
    cursor.execute(fetch_items_sitar_india)
    for row in cursor.fetchall():
        items['item_'+str(i)] = row[0]
        i += 1
    print items
    context = {}
    context['food_items'] = items

    return render_to_response('generate_bill.html',  RequestContext(request, context))

def get_overall_averages(request):
    cursor = connection.cursor()
    averages = {'ambience':0, 'food quality':0, 'service':0, 'Overall Rating':0}

    for key in averages:
        cursor.execute("select 6 - avg(R.choice_id) from Survey S, Question Q, Response R where R.question_id = Q.id and Q.text=\"" + key + "\";")
        result = cursor.fetchall()
        averages[key] = result[0][0]
    return JsonResponse(averages)

def get_favourite_items(request):
    favourite_items = {}
    cursor = connection.cursor()
    cursor.execute(
        "select U.first_name as fn, U.last_name as ln, U.email em, B.item_name it "
        + "from Survey S, Has_Bill B, Checkin C, User U "
        + "where C.survey_id = S.id and B.bill_id = C.bill_id and U.id = S.user_id and C.restaurant_id = \"testID\" "
        + "group by U.first_name, U.last_name, B.item_name "
        + "having count(*) >= all "
        + "( "
        + "select count(*) "
        + "from "
        + "Survey S1, Has_Bill B1, Checkin C1, User U1 "
        + "where C1.survey_id = S1.id and B1.bill_id = C1.bill_id and U1.id = S1.user_id and C1.restaurant_id = \"testID\" and U.first_name = U1.first_name and U.last_name = U1.last_name "
        + "group by U1.first_name, U1.last_name, B1.item_name);"
    )
    result = cursor.fetchall()
    i = 0
    for row in result:
        favourite_items["user_" + str(i)] = {}
        favourite_items["user_" + str(i)]["first_name"] = row[0]
        favourite_items["user_" + str(i)]["last_name"] = row[1]
        favourite_items["user_" + str(i)]["email"] = row[2]
        favourite_items["user_" + str(i)]["item"] = row[3]

    print favourite_items
    return JsonResponse(favourite_items)

def user_likings(request):
    restaurant_id = "testID"
    print "Inside User likings"
    cursor = connection.cursor()
    query = "select concat(10*floor(age/10), '-', 10*floor(age/10) + 10) as `ranges`, count(*) as count\
            from (select ROUND(DATEDIFF(curdate(),dob ) / 365.25) as age\
            from User where id in (select distinct user_id from Survey s, Checkin c where s.id = c.survey_id\
            and c.restaurant_id = \"" + restaurant_id + "\"))as t group by `ranges`\
            ORDER   BY `count` DESC LIMIT 1;"
    #print query
    cursor.execute(query)
    row = cursor.fetchone()
    values = str(row[0]).split("-")
    print values[0],values[1]
    start_age = values[0]
    end_age = values[1]

    query = "select u.id,c.bill_id \
            from User u, Checkin c, Survey s where u.id = s.user_id and s.id = c.survey_id\
            and s.restaurant_id = \"" + restaurant_id + "\" and ROUND(DATEDIFF(curdate(),u.dob ) / 365.25) between " +  start_age + " and " + end_age + ";"
    print query
    cursor.execute(query)
    bill_ids = "("
    for row in cursor.fetchall():
        print row[0],row[1]
        bill_ids+= str(row[1]) + ","
        items_in_bill = ""
    bill_ids = bill_ids[:-1]
    bill_ids+= ")"
    print bill_ids

    query = "select item_name, count(*) as count from Has_Bill \
    where bill_id in" + bill_ids + "group by item_name order by count desc limit 1;"
    print query
    cursor.execute(query)
    row = cursor.fetchone()
    print row[0]
    return HttpResponse("")

@csrf_exempt
@require_POST
def get_overall_averages(request):
    cursor = connection.cursor()
    averages = {'ambience':0, 'food quality':0, 'service':0, 'Overall Rating':0}

    for key in averages:
        cursor.execute("select 6 - avg(R.choice_id) from Survey S, Question Q, Response R where R.question_id = Q.id and Q.text=\"" + key + "\";")
        result = cursor.fetchall()
        averages[key] = result[0][0]
    return JsonResponse(averages)

@csrf_exempt
def get_no_checkins(request):
    request.session['restaurant_id'] = 'testID'
    restaurant_id = request.session['restaurant_id']
    checkins_10days = {'count':0}
    no_checkins = 'select count(*) from Checkin where restaurant_id=\''+restaurant_id+'\' and bill_id in (select id from Bill where time_stamp > date_sub(now(), interval 10 day) and restaurant_id=\''+restaurant_id+'\');'
    print no_checkins
    cursor = connection.cursor()
    cursor.execute(no_checkins)
    row = cursor.fetchone()
    checkins_10days['count'] = row[0]
    print row[0]
    return JsonResponse(checkins_10days)