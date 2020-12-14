from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from .forms import EmployeeForm, Employee

class EmployeeImage(TemplateView):
    form = EmployeeForm
    template_name = 'imageHotel/emp_image.html'

    def post(self, request, *args, **kwargs):
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('home', kwargs={'pk': ojb }))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)



class EmpImageDisplay(DetailView):
    model = Employee
    template_name = 'imageHotel/emp_image_display.html'
    context_object_name = 'emp'