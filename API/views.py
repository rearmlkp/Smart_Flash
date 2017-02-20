# from .serializers import UserSerializer, GroupSerializer
import hashlib

import nltk
import numpy
import pandas
from keras.layers import Dense
from keras.models import Sequential
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.response import Response
from rest_framework_xml.renderers import XMLRenderer

from .models import Card, User, Deck
from .serializers import CardSerializer, DeckSerializer, UserSerializer

seed = 7
numpy.random.seed(seed)

arr = {}
y = {}

code = 150


def process(card):
    front_tag = nltk.pos_tag(nltk.word_tokenize(card.front))
    back_split = nltk.word_tokenize(card.back)
    pos = 0
    y_add = []
    while pos < len(back_split):
        if (back_split[pos] == '<') and (back_split[pos + 1] == 'hide'):
            pos += 3
            while (pos < len(back_split)) and (back_split[pos] != '<'):
                y_add.append(1.)
                pos += 1
            pos += 3
        else:
            y_add.append(0.)
            pos += 1
    count = {}
    all_tag = {}
    pos = 0
    for k in front_tag:
        c = int(hashlib.sha1(k[0].encode('utf-8')).hexdigest(), 16) % code
        t = k[1]
        if not (t in count):
            count[t] = 0
        else:
            count[t] += 1
        t = t + "_" + str(count[t])
        if arr[t] == 1:
            arr[t] = [c]
            y[t] = [y_add[pos]]
            pos += 1
        else:
            arr[t].append(c)
            y[t].append(y_add[pos])
            pos += 1
        all_tag[t] = 1
    for key in arr:
        if not (key in all_tag):
            c = int(hashlib.sha1(''.encode('utf-8')).hexdigest(), 16) % code
            if arr[key] == 1:
                arr[key] = [c]
                y[key] = [0.]
            else:
                arr[key].append(c)
                y[key].append(0.)


# Find all tags available:

for card in Card.objects.all():
    front_tag = nltk.pos_tag(nltk.word_tokenize(card.front))
    count = {}
    for k in front_tag:
        t = k[1]
        if not (t in count):
            count[t] = 0
        else:
            count[t] += 1
        t = t + "_" + str(count[t])
        arr[t] = 1
        y[t] = 1

for card in Card.objects.all():
    process(card)

# print(arr)
# print(y)

model = Sequential()
model.add(Dense(len(arr) * 10, input_dim=len(arr), activation='relu'))
model.add(Dense(len(arr) * 5, activation='relu'))
model.add(Dense(len(arr), activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

x = pandas.DataFrame(arr)
y = pandas.DataFrame(y)
print(x.columns.values)
# print(x)

model.fit(x.values, y.values, nb_epoch=100, batch_size=100, verbose=0)
print(model.evaluate(x.values, y.values))
pred = model.predict(x.values)


def predict_tag(front):
    front_tag = nltk.pos_tag(nltk.word_tokenize(front))
    count = {}
    all_tag = {}
    arr2 = {}
    for k in front_tag:
        c = int(hashlib.sha1(k[0].encode('utf-8')).hexdigest(), 16) % code
        t = k[1]
        if not (t in count):
            count[t] = 0
        else:
            count[t] += 1
        t = t + "_" + str(count[t])
        arr2[t] = [c]
        all_tag[t] = 1
    for key in arr:
        if not (key in all_tag):
            arr2[key] = int(hashlib.sha1(''.encode('utf-8')).hexdigest(), 16) % code
    if len(arr2) > len(arr):
        return [-1, -1]
    line = pandas.DataFrame(arr2)
    # print(line.values)
    pred = model.predict(line.values)
    return pred


def hide(front, pred):
    front_token = nltk.word_tokenize(front)
    front_tag = nltk.pos_tag(front_token)
    count = {}
    for i in range(0, len(front_tag)):
        k = front_tag[i]
        t = k[1]
        if not (t in count):
            count[t] = 0
        else:
            count[t] += 1
        t = t + "_" + str(count[t])
        cols = y.columns.values
        pos = -1
        for j in range(0, len(cols), 1):
            if cols[j] == t:
                pos = j
                break
        if pos != -1:
            if pred[pos] > 0.7:
                front_token[i] = '<hide>' + front_token[i] + '</hide>'
    return " ".join(front_token)


# ==========================================================================================================

@api_view(['GET', 'POST'])
@renderer_classes((XMLRenderer,))
def card_list(request, pk):
    try:
        deck = Deck.objects.get(pk=pk)
    except Deck.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        try:
            cards = Card.objects.filter(deck__in=deck)
        except Card.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        if ('type' in data) and ('front' in data) and ('back' in data):
            card = Card(type=data['type'], front=data['front'], back=data['back'])
            card.save()
            # TODO: Add to deck after save
            return Response(status=status.HTTP_201_CREATED)
        if ('back' not in data) and ('front' in data):
            front = data['front']
            result = predict_tag(front)
            if len(result) == 2:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            back = hide(front, result[0])
            data['back'] = back
            card = Card(type=data['type'], front=data['front'], back=data['back'])
            card.save()
            # TODO: Add to deck after save
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@renderer_classes((XMLRenderer,))
def card_detail(request, pk):
    try:
        card = Card.objects.get(pk=pk)
    except Card.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        serializer = CardSerializer(card)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def login(request):
    print(request.data)
    username = request.data['username']
    password = request.data['password']
    try:
        _ = User.objects.get(username=username, password=password)
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def create_user(request):
    username = request.data['username']
    password = request.data['password']
    try:
        _ = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username, password=password)
        user.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes((XMLRenderer,))
def get_users_deck(request):
    username = request.data['username']
    try:
        decks = Deck.objects.filter(user__username__exact=username)
    except Deck.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = DeckSerializer(decks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_deck(request):
    try:
        user = User.objects.get(username=request.data['username'])
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    deck = Deck(name=request.data['deck_name'], user=user)
    deck.save()
    return Response(status=status.HTTP_201_CREATED)

# TODO: Edit, Delete deck API
