import os
from os import listdir
from os.path import join
from os.path import isfile

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic import TemplateView

from inference.forms import FileForm
from inference.models import FileModel

# Main Tasks
from inference.taskMain import mosaic


class ImageResultList(ListView):
    """
    This view will show all the file are processed.
    """
    model = FileModel
    template_name = 'results_list.html'
    queryset = FileModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_path = settings.RESULT_ROOT
        myfiles = [f for f in listdir(media_path) if isfile(join(media_path, f))]
        context['filename'] = myfiles
        return context


class ProcessSuccessViewMosaic(TemplateView):
    template_name = 'process_success.html'


class UploadSuccessView(TemplateView):
    template_name = 'upload_success.html'


class ProcessSuccessView(TemplateView):
    template_name = 'process_success.html'


def delete_mosaic(request, pk):
    if request.method == 'POST':
        hdr = FileModel.objects.get(pk=pk)
        hdr.delete()
    return redirect('manage_uploaded_mosaic')


def upload_mosaic_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mosaic/upload_success_mosaic/')
    else:
        form = FileForm()
    return render(request, 'post_file.html', {'form': form})


def process_mosaic(request, pk):
    if request.method == 'POST':
        a = FileModel.objects.get(pk=pk)
        file_name = str(a.file)
        file_path = str(a.path)
        file_abslute = os.path.join(file_path,file_name)
        print(file_abslute)
        print(file_name)
        print(file_path)
        tiles_path = ''
        get_folder = os.path.join(settings.MEDIA_ROOT, tiles_path)
        mosaic(file_abslute,get_folder)
        print("Completed.")
    return redirect('process_success_mosaic')


class MosaicListView(ListView):
    model = FileModel
    template_name = 'list_mosaic.html'
    context_object_name = 'mosaics'


class MosaicListViewProcess(ListView):
    model = FileModel
    template_name = 'select_file_predictions.html'
    context_object_name = 'mosaics'
