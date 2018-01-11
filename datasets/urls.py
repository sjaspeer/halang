from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from datasets import views
import simplejson

app_name= 'datasets'

urlpatterns = [
    # /
    url(r'^$', views.IndexView, name='index'),

    # /signup
    url(r'^signup/$', views.signup, name='signup'),

    # /signin
    url(r'^signin/$', views.signin, name='signin'),

    # /signout
    url(r'^signout/$', views.signout, name='signout'),

    # /api/datasets/
    url(r'^api/datasets/$', 
        views.DataSetList.as_view({'get': 'list', 'post': 'create'}), 
        name='dataset-list'
        ),
    url(r'^api/datasets/(?P<pk>[0-9]+)/$', 
        views.DataSetList.as_view({
            'get': 'retrieve', 'put': 'update', 
            'patch': 'partial_update', 'delete': 'destroy'
            }), 
        name='dataset-detail'
        ),

    # /user/1/
    url(r'^user/(?P<pk>[0-9]+)/$', views.ProfileView, name='profile'),

    # /user/1/edit
    url(r'^user/(?P<pk>[0-9]+)/edit/$', views.EditProfileView, name='editprofile'),

    # /user/1/changepassword
    url(r'^user/(?P<pk>[0-9]+)/password/$', views.ChangePasswordView, name='changepassword'),

    # /data/
    url(r'^data/$', views.DataView.as_view(), name='data'),

    # /data/1/
    url(r'^data/(?P<pk>[0-9]+)/$', views.DataDetailView, name='datadetail'),

    # /data/1/edit
    url(r'^data/(?P<pk>[0-9]+)/edit/$', views.EditDataSetView, name='editdataset'),

    # /data/1/download/json
    url(r'^data/(?P<pk>[0-9]+)/download/json/$', views.DownloadJsonView.as_view(), name='downloadJson'),

    # /data/1/download/csv
    url(r'^data/(?P<pk>[0-9]+)/download/csv/$', views.DownloadCsvView.as_view(), name='downloadCsv'),

    # /data/1/adddata
    url(r'^data/(?P<pk>[0-9]+)/adddata/$', views.AddDataView, name='adddata'),

    # /data/1/editrecord/1
    url(r'^data/(?P<pk>[0-9]+)/editrecord/(?P<number>[0-9]+)/$', views.editRecordView, name='editrecord'),

    # /data/1/deleterecord/1
    url(r'^data/(?P<pk>[0-9]+)/deleterecord/(?P<number>[0-9]+)/$', views.deleteRecordView, name='deleterecord'),

    # /mydata/
    url(r'^mydata/$', views.MyDataView, name='mydata'),

    # /newdata/
    url(r'^newdata/$', views.NewDataView, name='newdata'),

    # /newdata2/
    url(r'^newdata2/(?P<number>[0-9]+)/$', views.NewData2View, name='newdata2'),

    # /about/
    url(r'^team/$', views.AboutView, name='about'),

    # /whatwedo/
    url(r'^whatwedo/$', views.WhatWeDoView, name='whatwedo'),


    # # /data/1/getcsv/
    # url(r'^data/(?P<pk>[0-9]+)/getcsv/$', views.GetCsvView.as_view(), name='getcsv'),
    #
    # # /data/1/getjson/
    # url(r'^data/(?P<pk>[0-9]+)/getjson/$', views.GetJsonView.as_view(), name='getjson'),

]

urlpatterns = format_suffix_patterns(urlpatterns)