import requests
import xmltodict
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


# TODO: implement logout

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
    schema = open('Schema/deck_schema.xsd', 'r')
    xmlschema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xml_doc = etree.XML(r.content)
    print(xmlschema.validate(xml_doc))
    if xmlschema.validate(xml_doc):
        # TODO: Create XSLT file to test
        xslt = open('XSLT/decks_xslt.xsl')
        transform = etree.XSLT(xslt)
        result = transform(xml_doc)
        return render(request, 'homepage.html', {
            'data': str(result)
        })


def create_deck(request):
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


def deck_detail(request, pk):
    if request.method == 'GET':

    else:

# TODO: Deck view: Add a card, edit card, render cards using xslt
