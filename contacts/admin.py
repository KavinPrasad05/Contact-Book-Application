from django.contrib import admin
from .models import ContactGroup, Contact  


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display  = ['name']          
    search_fields = ['name']         


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone_number', 'email', 'contact_group']  
    list_filter   = ['contact_group']                                    
    search_fields = ['name', 'phone_number', 'email']                  