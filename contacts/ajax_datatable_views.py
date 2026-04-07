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
            'className':  'text-center',
        },
    ]

    def customize_row(self, row, obj):
        # Email fallback  
        if not obj.email:
            row['email'] = '<span class="text-muted">—</span>'

        # Action buttons  
        row['actions'] = (
            f'<button class="btn btn-success btn-sm btn-edit" '
            f'        data-id="{obj.pk}" title="Edit">'
            f'  <i class="bi bi-pencil-square"></i>'
            f'</button> '
            f'<button class="btn btn-danger btn-sm btn-delete" '
            f'        data-id="{obj.pk}" '
            f'        data-name="{obj.name}" title="Delete">'
            f'  <i class="bi bi-trash"></i>'
            f'</button>'
        )
        return