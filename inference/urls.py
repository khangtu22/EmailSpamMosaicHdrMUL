from django.urls import path
from . import views
from django.conf.urls import url

from inference.views import UploadSuccessView, ImageResultList, MosaicListView, MosaicListViewProcess, ProcessSuccessViewMosaic

urlpatterns = [
    path('home_mosaic/', views.upload_mosaic_file, name='home_mosaic'),
    path('delete_mosaic/<int:pk>/', views.delete_mosaic, name='mosaic_delete'),
    path('manageuploaded_mosaic/', MosaicListView.as_view(), name='manage_uploaded_mosaic'),
    path('process_success_mosaic/', ProcessSuccessViewMosaic.as_view(), name='process_success_mosaic'),
    path('upload_success_mosaic/', UploadSuccessView.as_view(), name='upload_success_mosaic'),
    path('process_mosaic/<int:pk>', views.process_mosaic, name='process_mosaic'),
    url('viewresult/', ImageResultList.as_view(), name='result_list'),
    path('select_process_mosaic/', MosaicListViewProcess.as_view(), name='select_process_mosaic'),
]