import requests
from lxml import etree
from django.shortcuts import render
from rest_framework import status

localhost = "http://127.0.0.1"
API_port = '8000'

API_url = localhost + ":" + API_port + "/"

# This FUCKING work, thanks pycharm!
some_xml_data = "<root>data</root>"
root = etree.XML(some_xml_data)
print(root.tag)


# Create your views here.
def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        r = requests.post(API_url + "login/", data={
            'username': username,
            'password': password
        })
        if r.status_code == status.HTTP_200_OK:
            request.session['username'] = username
            return homepage(request)
        return render(request, 'index.html', {
            'error_message': "User doesn't exist!"
        })
    elif request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'index.html')
        return homepage(request)


def logout(request):
    del request.session['username']
    request.session.modified = True
    return render(request, 'index.html')


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        r = requests.post(API_url + 'register/', data={
            'username': username,
            'password': password
        })
        if r.status_code == status.HTTP_201_CREATED:
            return render(request, 'index.html')
        return render(request, 'register.html', {
            'error_message': "User exist!"
        })


def homepage(request):
    username = request.session['username']
    r = requests.post(API_url + "decks/", data={
        'username': username,
    })
    if r.status_code == status.HTTP_400_BAD_REQUEST:
        return render(request, 'homepage.html', {
            'error_message': "User doesn't have any deck (yet)"
        })

    # XML validation:
    schema_file = open('Schema/deck_schema.xsd', 'r')
    schema_file = etree.parse(schema_file)
    xmlschema = etree.XMLSchema(schema_file)
    xml_doc = etree.XML(r.content)
    print(xmlschema.validate(xml_doc))
    if xmlschema.validate(xml_doc):
        xslt_file = open('XSLT/decks_xslt.xsl', 'r')
        xslt_file = etree.parse(xslt_file)
        transform = etree.XSLT(xslt_file)
        result = transform(xml_doc)
        return render(request, 'homepage.html', {
            'data': str(result)
        })
    else:
        return render(request, 'homepage.html', {
            'error_message': "error while validating XML"
        })


def deck_create(request):
    username = request.session['username']
    r = requests.post(API_url + "decks/create/", data={
        'username': username,
        'deck_name': request.POST['deck_name']
    })
    if r.status_code != status.HTTP_201_CREATED:
        return render(request, 'homepage.html', {
            'error_message': "Can't create deck!"
        })
    return homepage(request)

# TODO: Edit, Delete decks

# def deck_detail(request, pk):
#     if request.method == 'GET':
#
#     else:

# TODO: Deck view: Add a card, edit card, render cards using xslt
