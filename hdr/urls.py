from django.urls import path
from . import views
from .views import UploadSuccessViewHdr, ProcessSuccessViewHdr, \
    ImageResultListHdr, HdrListView

urlpatterns = [
    path('home_hdr/', views.upload_file, name='home_hdr'),
    path('upload_success_hdr/', UploadSuccessViewHdr.as_view(), name='upload_success_hdr'),
    path('process_success_hdr/', ProcessSuccessViewHdr.as_view(), name='process_success_hdr'),
    path('viewresult_hdr/', ImageResultListHdr.as_view(), name='result_list_hdr'),
    path('manageuploaded_hdr/', HdrListView.as_view(), name='manage_uploaded_hdr'),
    path('manageuploaded_hdr/<int:pk>/', views.delete_hdr, name='hdr_delete_1'),
    path('process_hdr/', views.process_hdr, name='process_hdr'),
]