from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import DataSet, Profile
from .serializers import DataSetSerializer
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .forms import DataSetForm, ColumnForm, DataForm, SignUpForm, deleteRecordForm, UserForm, ProfileForm
from django.contrib.auth import login, logout, authenticate
from django.core.urlresolvers import reverse
from django.views import generic
import os
from django.conf import settings
import simplejson
import psycopg2
from django.contrib.auth.views import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .mixins import UserIsOwnerMixin
from .permissions import IsOwner
import os
from urllib import parse

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])


#cur = conn.cursor()
# Lists all datasets
# 
class DataSetList(ModelViewSet):
    permission_classes = (IsOwner, IsAuthenticated)
    serializer_class = DataSetSerializer
    queryset = DataSet.objects.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = []
        return super(self.__class__, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save()


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('datasets:signin'))
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'signup.html', context)


def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('datasets:index'))
    else:
        return login(request, template_name='signin.html')


def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'signout.html')
    else:
        return HttpResponseRedirect(reverse('datasets:index'))


def IndexView(request):
    return render(request, 'index.html')


class DataView(generic.ListView):
    template_name = 'data.html'
    context_object_name = 'all_dataset'

    def get_queryset(self):
        combined_queryset = DataSet.objects.filter(DataSet_Status='Approved') | DataSet.objects.filter(DataSet_Status='Not yet Approved')
        return combined_queryset.order_by('-DataSet_Posted', '-id')


def DataDetailView(request, pk):
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    try:
        idvalues = []
        dataset = DataSet.objects.get(pk=pk)
        cur = conn.cursor()
        title = DataSet.objects.get(id=pk)
        #python object
        cur.execute("""SELECT * FROM "{}" ORDER BY id;""".format(title.id))
        rows = cur.fetchall()
        count = len(rows)
        colnames=[desc[0] for desc in cur.description]
        count2 = len(colnames)
        for i in rows:
            for o in i:
                if i.index(o) == 0:
                    idvalues.append(o)
                    break
        newvalues = list(range(1,len(idvalues)+1))

        for newvalue, idvalue in zip(newvalues, idvalues):
            cur.execute("""UPDATE "{}" SET id = '{}' WHERE id={};""".format(title.id, newvalue, idvalue))
            conn.commit();
        #csv
        sql = """COPY "%s" TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
        with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
            cur.copy_expert(sql % title.id, file)
        csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
        csv = csvdata.readlines()
        #json
        cur.execute("""SELECT row_to_json("{}") FROM "{}" ORDER BY id;""".format(title.id, title.id))
        with open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "w") as file2:
            simplejson.dump(cur.fetchall(), file2)
        jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
        json = jsondata.readlines()
    finally:
        conn.close()

    context = {"dataset": dataset, "rows": rows, "colnames": colnames, "csv": csv, "json": json, "count": count, "count2": count2}
    return render(request, "datadetail.html", context)


class DownloadJsonView(APIView):

    def get(self, request, *args, **kwargs):
        conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
        pk = self.kwargs['pk']
        try:
            dataset = DataSet.objects.get(pk=pk)
            cur = conn.cursor()
            title = DataSet.objects.get(id=pk)
            #python object
            cur.execute("""SELECT * FROM "{}" ORDER BY id;""".format(title.id))
            rows = cur.fetchall()
            count = len(rows)
            colnames=[desc[0] for desc in cur.description]
            count2 = len(colnames)
            #json
            cur.execute("""SELECT row_to_json("{}") FROM "{}" ORDER BY id;""".format(title.id, title.id))
            with open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "w") as file2:
                simplejson.dump(cur.fetchall(), file2, indent=2)
            jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
            json = jsondata.readlines()
        finally:
            conn.close()

        jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
        response = HttpResponse(jsondata,content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename={}.json'.format(dataset.DataSet_Title)
        return response


class DownloadCsvView(APIView):

    def get(self, request, *args, **kwargs):
        conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
        pk = self.kwargs['pk']
        try:
            dataset = DataSet.objects.get(pk=pk)
            cur = conn.cursor()
            title = DataSet.objects.get(id=pk)
            #python object
            cur.execute("""SELECT * FROM "{}" ORDER BY id;""".format(title.id))
            rows = cur.fetchall()
            count = len(rows)
            colnames=[desc[0] for desc in cur.description]
            count2 = len(colnames)
            #csv
            sql = """COPY "%s" TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
            with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
                cur.copy_expert(sql % title.id, file)
            csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
            csv = csvdata.readlines()
        finally:
            conn.close()

        csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
        response = HttpResponse(csvdata,content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(dataset.DataSet_Title)
        return response


def MyDataView(request):
    if request.user.is_authenticated:
        all_dataset = DataSet.objects.filter(DataSet_Poster=request.user.id)
    else:
        pass

    context = {"all_dataset": all_dataset}
    return render(request, 'datasets.html', context)


def NewDataView(request):
    if request.method == 'POST':
        form = DataSetForm(data=request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.DataSet_Poster = request.user
            dataset.save()
            title = DataSet.objects.last()
            conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
            cur = conn.cursor()
            cur.execute("""CREATE TABLE "%s"(id serial PRIMARY KEY);""" % str(title.id))
            conn.commit();
            conn.close();
            cur.close();
            number = int(request.POST['noofcolumns'])

            return HttpResponseRedirect(reverse('datasets:newdata2', args=[number]))
    else:
        form = DataSetForm()

    context = {'form': form}
    return render(request, 'newdata.html', context)


def NewData2View(request, number):
    forms = [ColumnForm(data=request.POST or None) for x in range(int(number))]
    if request.method == 'POST':
        index = 0
        lastDataSet = DataSet.objects.last()
        for form in forms:
            if form.is_valid():
                columnname = request.POST.getlist('cname').pop(index)
                columntype = "VARCHAR"
                conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
                cur = conn.cursor()
                cur.execute("""ALTER TABLE "{}" ADD COLUMN "{}" {};""".format(lastDataSet.id, columnname, columntype))
                conn.commit();
                conn.close();
                cur.close();
                index=index+1

        return HttpResponseRedirect(reverse('datasets:datadetail', args=[lastDataSet.id]))

    context = {'forms': forms}
    return render(request, 'newdata2.html', context)


def AddDataView(request, pk):
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()
    title = DataSet.objects.get(id=pk)
    cur.execute("""SELECT * FROM "{}" ORDER BY id;""".format(title.id))
    colnames = [desc[0] for desc in cur.description]
    count = len(colnames)-1
    cnames = ''
    colname = [desc[0] for desc in cur.description]
    colname.remove('id')
    for x in colname:
        cnames = cnames + '"' + x + '", '
    cnames = cnames[:-2]

    forms = [DataForm(data=request.POST or None) for x in range(int(count))]
    if request.method == 'POST':
        for form in forms:
            if form.is_valid():
                values = ''
                for x in request.POST.getlist('dvalue'):
                    values = values + "'" + x + "', "
                values = values[:-2]
        cur = conn.cursor()
        cur.execute("""INSERT INTO "{}"({}) VALUES({});""".format(title.id, cnames, values))
        conn.commit();
        conn.close();
        cur.close();

        return HttpResponseRedirect(reverse('datasets:datadetail', args=[title.id]))

    context = {'forms': forms, "colnames": colname, "count": count, "cname": list(reversed(colname))}
    return render(request, 'adddata.html', context)


def editRecordView(request, pk, number):
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()
    title = DataSet.objects.get(id=pk)
    cur.execute("""SELECT * FROM "{}" WHERE id={} ;""".format(title.id, number))
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    count = len(colnames)-1
    cnames = ''
    colname = [desc[0] for desc in cur.description]
    colname.remove('id')
    for x in colname:
        cnames = cnames + '"' + x + '", '
    cnames = cnames[:-2]

    forms = [DataForm(data=request.POST or None) for x in range(int(count))]
    if request.method == 'POST':
        for form in forms:
            if form.is_valid():
                values = ''
                for x in request.POST.getlist('dvalue'):
                    values = values + "'" + x + "', "
                values = values[:-2]
        cur = conn.cursor()
        for cname, value in zip(colname, request.POST.getlist('dvalue')):
            cur.execute("""UPDATE "{}" SET {} = '{}' WHERE id={};""".format(title.id, cname, value, number))
            conn.commit();
        conn.close();
        cur.close();

        return HttpResponseRedirect(reverse('datasets:datadetail', args=[title.id]))

    context = {'forms': forms, "colnames": colname, "count": count, "cname": list(reversed(colname)), "rows": rows}
    return render(request, 'editrecord.html', context)


def deleteRecordView(request, pk, number):
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()
    title = DataSet.objects.get(id=pk)
    cur.execute("""SELECT * FROM "{}" WHERE id={} ;""".format(title.id, number))
    rows = cur.fetchall()

    if request.method == 'POST':
        form = deleteRecordForm(data=request.POST)
        if form.is_valid():
            conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
            cur = conn.cursor()
            title = DataSet.objects.get(id=pk)
            cur.execute("""DELETE FROM "{}" WHERE id={} ;""".format(title.id, number))
            conn.commit();
            conn.close();
            cur.close();

            return HttpResponseRedirect(reverse('datasets:datadetail', args=[title.id]))
    else:
        form = deleteRecordForm(data=request.POST)

    context = {'form': form, 'rows': rows}
    return render(request, 'deleterecord.html', context)


def AboutView(request):
    return render(request, 'about.html')

def WhatWeDoView(request):
    return render(request, 'whatwedo.html')

def ProfileView(request, pk):
    usertouse = User.objects.get(id=pk)
    profile = Profile.objects.get(user=pk)
    all_dataset = DataSet.objects.filter(DataSet_Poster=pk)

    context = {"usertouse": usertouse, "profile": profile, "all_dataset": all_dataset}
    return render(request, "profile.html", context)


def EditProfileView(request, pk):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return HttpResponseRedirect(reverse('datasets:profile', args=[pk]))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, 'editprofile.html', context)

def EditDataSetView(request, pk):
    dataset = get_object_or_404(DataSet, id=pk)
    
    if request.method == 'POST':
        form = DataSetForm(instance=dataset, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('datasets:data', args=[pk]))
    else:
        form = DataSetForm(instance=dataset)

    context = {"form": form, "dataset": dataset}
    return render(request, 'editdataset.html', context)

def ChangePasswordView(request, pk):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return HttpResponseRedirect(reverse('datasets:profile', args=[pk]))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {
        'form': form
    })


# class DataDetailView(generic.DetailView):
#     model = DataSet
#     template_name = 'datadetail.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
    #     conn = psycopg2.connect(
    #     database=url.path[1:],
    #     user=url.username,
    #     password=url.password,
    #     host=url.hostname,
    #     port=url.port
    # )
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         #python object
#         cur.execute("""SELECT * FROM {}""".format(title.DataSet_Title))
#         rows = cur.fetchall()
#         #csv
#         sql = """COPY %s TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
#             cur.copy_expert(sql % title.DataSet_Title, file)
#         csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
#         csv = csvdata.readlines()
#         #json
#         cur.execute("""SELECT row_to_json({}) FROM {};""".format(title.DataSet_Title, title.DataSet_Title))
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "w") as file2:
#             simplejson.dump(cur.fetchall(), file2, indent=2)
#         jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
#         json = jsondata.readlines()
#
#         conn.close();
#         cur.close();
#         context = {"rows": rows, "csv": csv, "json": json}
#         return context

# class GetCsvView(generic.DetailView):
#     model = DataSet
#     template_name = 'getcsv.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
#         conn = psycopg2.connect(
    #     database=url.path[1:],
    #     user=url.username,
    #     password=url.password,
    #     host=url.hostname,
    #     port=url.port
    # )
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         sql = """COPY %s TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
#             cur.copy_expert(sql % title.DataSet_Title, file)
#         conn.close();
#         cur.close();
#         fh = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
#         rows = fh.readlines()
#         context = {"rows": rows}
#
#         return context

# class GetJsonView(generic.DetailView):
#     model = DataSet
#     template_name = 'getjson.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
#         conn = psycopg2.connect(
    #     database=url.path[1:],
    #     user=url.username,
    #     password=url.password,
    #     host=url.hostname,
    #     port=url.port
    # )
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         cur.execute("""SELECT row_to_json({}) FROM {};""".format(title.DataSet_Title, title.DataSet_Title))
#         rows = cur.fetchall()
#         conn.close();
#         cur.close();
#         context = {"rows": rows}
#
#         return context

# class MyDataView(generic.ListView):
#     template_name = 'datasets.html'
#     context_object_name = 'all_dataset'
#
#     def get_queryset(self):
#         combined_queryset = DataSet.objects.filter(DataSet_Poster='1')
#         return combined_queryset.order_by('-DataSet_Posted', '-id')