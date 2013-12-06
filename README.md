This project actually a fork of datatables_demo 1.6.2 which is work with Django 1.6 and below. For more information checkout [1].
I integrated project with buildout and made it work with Django 1.3 and above.
You can easily integrate project with yours if you follow instructions on this readme document.


Django-Datatables
=======

Datatables-Datatables is a demonstration of the jQuery plug in, datatables with server side datasource from Django. The demonstration contains a working demoDjango project complete with HTML, CSS and Javascript needed to implement a complete working same.

How To Install
======

    $ sudo apt-get install git
    $ git clone git://github.com/farukuzun/Django-Datatables.git
    $ cd Django-Datatables
    $ python bootstrap.py
    $ ./bin/buildout
    $ ./bin/django runserver

Usage
======

To implement this code into your application, follow these steps:

Create an entry in urls.py and views.py that will server the HTML and JS needed for datatables
Create a separate url and view for returning a json object to datatables.

    def get_surveys(request):
    querySet = Survey.objects.all()
    columnIndexNameMap = { 0: 'id', 1 : 'name', 2: 'description', 3: 'active', 4: 'created' }
    jsonTemplatePath = 'qa/survey/json_surveys.txt'
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)

1. Create a  queryset object for the model you wish the data to be drawn from (querySet)
2. Create a dict for the column names, in correct display order (columnIndexNameMap)
3. Return the response to get_datatables_records which is contained in utils.py
