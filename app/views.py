from django.shortcuts import render
from django.http import HttpResponse
import datetime

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def get_table_list(self, cursor):
    "Returns a list of table names in the current database."
    cursor.execute("SELECT count(*) FROM Review")
    return [row[0].lower() for row in cursor.fetchall()]