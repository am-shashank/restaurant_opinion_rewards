from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
from django.db import connection
from datetime import datetime
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
    filename = "business/database_images/qr_code/"+restaurant_name + '_' + bill_id+'.png'
    text = 'restaurant_name:'+restaurant_name+'\n\
    bill_id:'+bill_id+'\n\
    item1:'+item1+'; quantity:'+quantity1+'; price:'+price1+'\n\
    item2:'+item2+'; quantity:'+quantity2+'; price:'+price2+'\n\
    total:'+total+'\n\
    time:'+str(datetime.now().time().hour)
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