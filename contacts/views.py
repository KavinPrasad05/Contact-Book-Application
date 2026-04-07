from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy

from .models import Contact, ContactGroup
from .forms import ContactForm
from .ajax_datatable_views import ContactAjaxDatatableView

#  Contact List Page

class ContactListView(ListView):
    model               = Contact
    template_name       = 'contacts/contact_list.html'
    context_object_name = 'contacts'

    def get_context_data(self, **kwargs):
        context           = super().get_context_data(**kwargs)
        context['form']   = ContactForm()
        context['groups'] = ContactGroup.objects.all()
        return context

#  DataTables AJAX endpoint

class ContactDatatableView(ContactAjaxDatatableView):
    pass

#  Create Contact
#  No user assignment needed — user field removed from model

class ContactCreateView(CreateView):
    model       = Contact
    form_class  = ContactForm
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        contact = form.save()
        return JsonResponse({
            'success': True,
            'message': f'Contact "{contact.name}" created successfully!',
        })

    def form_invalid(self, form):
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)


#  Get single Contact to populate Edit modal

class ContactGetView(View):
    def get(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        return JsonResponse({
            'id':            contact.pk,
            'name':          contact.name,
            'phone_number':  contact.phone_number,
            'email':         contact.email or '',
            'contact_group': contact.contact_group_id,
            'picture_url':   contact.contact_picture.url
                             if contact.contact_picture else '',
        })


#  Update Contact

class ContactUpdateView(UpdateView):
    model       = Contact
    form_class  = ContactForm
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        updated = form.save()
        return JsonResponse({
            'success': True,
            'message': f'Contact "{updated.name}" updated successfully!',
        })

    def form_invalid(self, form):
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)


#  Delete Contact

class ContactDeleteView(DeleteView):
    model       = Contact
    success_url = reverse_lazy('contact_list')

    def delete(self, request, *args, **kwargs):
        contact = self.get_object()
        name    = contact.name
        contact.delete()
        return JsonResponse({
            'success': True,
            'message': f'Contact "{name}" deleted successfully!',
        })

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)