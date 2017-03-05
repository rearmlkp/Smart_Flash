import requests
from django.shortcuts import render
from lxml import etree
from rest_framework import status

localhost = "http://127.0.0.1"
API_port = '8000'

API_url = localhost + ":" + API_port + "/"


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
        xslt_file = open('XSLT/deck_xslt.xsl', 'r')
        xslt_file = etree.parse(xslt_file)
        transform = etree.XSLT(xslt_file)
        result = transform(xml_doc)
        return render(request, 'homepage.html', {
            'data': str(result),
            'username': username
        })
    else:
        return render(request, 'homepage.html', {
            'error_message': "error while validating XML",
            'username': username
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


def deck_edit_delete(request):
    if 'edit' in request.POST:
        r = requests.post(API_url + "decks/edit/" + request.POST['id'], data={
            'name': request.POST['name']
        })
        if r.status_code != status.HTTP_200_OK:
            return render(request, 'homepage.html', {
                'error_message': "Can't edit deck!"
            })
    else:
        r = requests.post(API_url + "decks/delete/" + request.POST['id'])
        if r.status_code != status.HTTP_200_OK:
            return render(request, 'homepage.html', {
                'error_message': "Can't edit deck!"
            })


# TODO: Deck view: Edit, Delete cards
def deck_detail(request, pk):
    r = requests.get(API_url + "decks/" + pk)
    if r.status_code != status.HTTP_200_OK:
        return render(request, 'deck.html', {
            'error_message': "You have no cards!",
            'pk': pk,
            'username': request.session['username']
        })
    # XML validation:
    schema_file = open('Schema/cards_schema.xsd', 'r')
    schema_file = etree.parse(schema_file)
    xmlschema = etree.XMLSchema(schema_file)
    xml_doc = etree.XML(r.content)
    if xmlschema.validate(xml_doc):
        xslt_file = open('XSLT/cards_xslt.xsl', 'r')
        xslt_file = etree.parse(xslt_file)
        transform = etree.XSLT(xslt_file)
        result = transform(xml_doc)
        return render(request, 'deck.html', {
            'data': str(result),
            'pk': pk,
            'username': request.session['username']
        })
    else:
        return render(request, 'deck.html', {
            'error_message': "error while validating XML",
            'pk': pk,
            'username': request.session['username']
        })


def create_card(request, pk):
    if request.method == 'POST':
        data = {
            'front': request.POST['front'],
            'back': request.POST['back'],
            'type': 0
        }
        if request.POST['back'] == '':
            del data['back']
        r = requests.post(API_url + "decks/" + pk, data=data)
        if r.status_code == status.HTTP_201_CREATED:
            return deck_detail(request, pk)
        else:
            return deck_detail(request, pk)
    else:
        return render(request, 'homepage.html')


def review(request, pk):
    r = requests.get(API_url + "decks/review/" + pk)
    if r.status_code == status.HTTP_200_OK:
        xml_doc = etree.XML(r.content)
        fronts = xml_doc.xpath('/root/list-item/front')
        backs = xml_doc.xpath('/root/list-item/back')
        displays = []
        words = []
        for i in range(len(fronts)):
            j = 0
            words.append([])
            display = ''
            while j < len(backs[i].text):
                if backs[i].text[j] == '<':
                    word = ''
                    j += 6
                    while backs[i].text[j] != '<':
                        word += backs[i].text[j]
                        display += '_'
                        j += 1
                    words[i].append(word)
                    j += 6
                else:
                    display += backs[i].text[j]
                j += 1
            displays.append(display)
        return render(request, 'review.html', context={
            'displays': displays,
            'words': words,
            'pk': pk,
            'username': request.session['username']
        })
