import ajax_datatable
from .models import Contact


class ContactAjaxDatatableView(ajax_datatable.AjaxDatatableView):
    model         = Contact
    title         = 'Contacts'
    column_defs = [
        {
            'name':    'id',
            'visible': False,
        },
        {
            'name':      'name',
            'title':     'Name',
            'visible':   True,
            'className': 'text-center',
        },
        {
            'name':      'phone_number',
            'title':     'Phone Number',
            'visible':   True,
            'className': 'text-center',
        },
        {
            'name':      'email',
            'title':     'Email',
            'visible':   True,
            'className': 'text-center',
        },
        {
            'name':       'actions',
            'title':      'Actions',
            'visible':    True,
            'orderable':  False,
            'searchable': False,
            'foreign_field': None,
            'className':  'text-center',
        },
    ]

    def customize_row(self, row, obj):
        # Email fallback  
        if not obj.email:
            row['email'] = '<span class="text-muted">—</span>'
        
        user = self.request.user  #get the currently logged-in user from the request.
        edit_btn = ''
        delete_btn = ''

        if user.can_update():
            edit_btn = (
                f'<button class="btn btn-success btn-sm btn-edit" '
                f'        data-id="{obj.pk}" title="Edit">'
                f'  <i class="bi bi-pencil-square"></i>'
                f'</button> '
            )
        
        if user.can_delete():
            delete_btn = (
                f'<button class="btn btn-danger btn-sm btn-delete" '
                f'        data-id="{obj.pk}" '
                f'        data-name="{obj.name}" title="Delete">'
                f'  <i class="bi bi-trash"></i>'
                f'</button>'
            )
        
        if not edit_btn and not delete_btn:
            row['actions'] = '<span class="text-muted fst-italic">View only</span>'
        else:
            row['actions'] = edit_btn + delete_btn

        return row  

        