import os
from os import listdir
from os.path import join
from os.path import isfile

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic import TemplateView

from hdr.models import FileHdrModel
from .form import UploadFileForm

# Main Tasks
from hdr.mainTaskHdr import run


class ImageResultListHdr(ListView):
    """
    This view will show all the file are processed.
    """
    model = FileHdrModel
    template_name = 'results_hdr_list.html'
    queryset = FileHdrModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_path = settings.HDR_ROOT
        myfiles = [f for f in listdir(media_path) if isfile(join(media_path, f))]
        context['filename'] = myfiles
        return context


class UploadSuccessViewHdr(TemplateView):
    template_name = 'upload_hdr_success.html'


class ProcessSuccessViewHdr(TemplateView):
    template_name = 'process_hdr_success.html'


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = str(request.FILES['file'])
            expose_time_value = str(request.POST['expose_time'])
            name_list_file = 'list.txt'
            path = os.path.join(settings.MEDIA_ROOT, name_list_file)
            f = open(name_list_file, 'a')
            f.write(file_name + " " + expose_time_value + "\n")
            print("Written \"" + file_name + " " + expose_time_value + "\" on file list.txt")
            f.close()
            form.save()
            return HttpResponseRedirect('/hdr/upload_success_hdr/')
    else:
        form = UploadFileForm()
    return render(request, 'post_hdr_file.html', {'form': form})


def delete_hdr(request, pk):
    if request.method == 'POST':
        hdr = FileHdrModel.objects.get(pk=pk)
        file_name = str(hdr.file)
        expose_time_value = str(hdr.expose_time)
        line_name = file_name + " " + expose_time_value
        f = open('list.txt', 'r')
        lines = f.readlines()
        f.close()
        new_file = open("list.txt", "w")
        for line in lines:
            if line.strip("\n") != line_name:
                new_file.write(line)
        new_file.close()
        hdr.delete()

        return redirect('manage_uploaded_hdr')


def process_hdr(request):
    if request.method == 'POST':
        run()
        print("Completed.")
    return redirect('process_success_hdr')


class HdrListView(ListView):
    model = FileHdrModel
    template_name = 'list_hdr.html'
    context_object_name = 'hdrs'

