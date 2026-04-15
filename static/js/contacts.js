$(document).ready(function () {

    //  CSRF: inject into every $.ajax POST automatically

    $.ajaxSetup({
        headers: { 'X-CSRFToken': CSRF_TOKEN }
    });

    //  URL HELPER
    //  Replaces the '/0/' placeholder with the real ID

    function getUrl(key, id) {
        return URLS[key].replace('/0/', '/' + id + '/');
    }

    //  SWEETALERT2 HELPER
    function showAlert(title, text, icon, color) {
        Swal.fire({
            title:              title,
            text:               text,
            icon:               icon,               // success, error, warning, info
            confirmButtonColor: color || '#198754',
            timer:              2000,
            showConfirmButton:  false,
            timerProgressBar:   true,               // shows a progress bar at the bottom
        });
    }

    //  SELECT2 INITIALIZATION
    //  context = the modal or container to search inside

    function initSelect2(context) {
        $('select', context).each(function () {
            var $s = $(this);

            // Destroy existing instance before re-initializing
            if ($s.hasClass('select2-hidden-accessible')) {
                $s.select2('destroy');
            }

            $s.select2({
                theme: 'bootstrap-5',
                width: '100%',
                // Attach to modal so dropdown is not clipped
                // by the modal's overflow:hidden
                dropdownParent: $s.closest('.modal').length
                    ? $s.closest('.modal')
                    : $('body'),
                placeholder: $s.find('option[value=""]').text() || '-- Select --',
                allowClear:  true
            });
        });
    }

    // Initialize Select2 after the modal becomes visible
    // (Select2 needs the element visible to calculate width)
    $('#contactModal').on('shown.bs.modal', function () {
        initSelect2($(this));
    });


    //  DATATABLES INITIALIZATION
    //  serverSide: true → django-ajax-datatable handles
    //  pagination, sorting, and searching on the server

    var table = $('#contactTable').DataTable({
        serverSide: true,
        processing: true,
        ajax: {
            url:  URLS.datatable,
            type: 'GET',
        },
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, 'All']],
        // Column order must match ContactAjaxDatatableView.column_defs
        columns: [
            { data: 'name' },
            { data: 'phone_number' },
            { data: 'email' },
            { data: 'actions', orderable: false, searchable: false },
        ],
        order: [[0, 'asc']], // Default sort by Name ascending
        language: {
            processing: '<div class="spinner-border text-primary" role="status"></div>',
            emptyTable: '<i class="bi bi-inbox fs-5 me-2"></i>No contacts found.',
        },
        columnDefs: [
            { targets: '_all', className: 'align-middle text-center' },
        ],
    });

    // Reload DataTable data after any CRUD operation
    // false = keep the user on the current page
    function refreshTable() {
        table.ajax.reload(null, false);
    }

    function showCurrentPicture(pictureUrl) {
        if (!pictureUrl) {
            hideCurrentPicture();
            return;
        }
        // Extract just the filename from the full URL path
        // e.g. '/media/contact_pictures/photo.jpg' → 'photo.jpg'
        var filename = pictureUrl.split('/').pop();
        $('#currentPictureName').text(filename);
        $('#currentPictureBox').removeClass('d-none');

        // Hide the file input — user must click Clear first
        // before they can upload a new picture
        $('#id_contact_picture').closest('.mb-3').find('input[type="file"]').hide();
    }
    function hideCurrentPicture() {
        $('#currentPictureBox').addClass('d-none');
        $('#currentPictureName').text('');
        // Show the file input again
        $('#id_contact_picture').closest('.mb-3').find('input[type="file"]').show();
    }
     $('#clearPictureBtn').on('click', function () {
        hideCurrentPicture();
        // Reset the file input value so no old file is carried over
        $('#id_contact_picture').val('');
        // Mark picture as cleared so views.py does not keep the old one
        $('#contactForm').data('picture-cleared', true);
    });

    //  VALIDATION HELPERS
    // Clears all error states before showing fresh errors

    function clearErrors() {
        // Remove red border from all inputs
        $('#contactForm .form-control, #contactForm .form-select')
            .removeClass('is-invalid');

        // Remove red border from Select2 containers
        $('#contactForm .select2-container .select2-selection')
            .css('border-color', '');

        // Hide all error message divs
        $('[id^="error-"]').text('').removeClass('show');
    }

    // Displays Django's validation errors on the correct fields
    function showErrors(errors) {
        $.each(errors, function (field, msg) {

            // Find input by id (e.g. #id_name) or fallback to name attribute
            var $field = $('#id_' + field);
            if (!$field.length) {
                $field = $('#contactForm [name="' + field + '"]');
            }
            $field.addClass('is-invalid');

            // For Select2 dropdowns, highlight the container too
            if ($field.is('select')) {
                $field.next('.select2-container')
                      .find('.select2-selection')
                      .css('border-color', '#dc3545');
            }

            // Show error message text below the field
            $('#error-' + field).text(msg).addClass('show');
        });
    }

    //  OPEN MODAL
    //  mode = 'create' → blank form
    //  mode = 'edit'   → fetch data then open form

    function openModal(mode, id) {
        // Always reset the form before opening
        $('#contactForm')[0].reset();
        $('#contactId').val('');
        $('#contactForm').data('picture-cleared', false); // reset cleared flag
        hideCurrentPicture();
        clearErrors();

        if (mode === 'create') {
            // Add mode 
            $('#modalTitle').html('<i class="bi bi-person-plus"></i> Add Contact');
            $('#modalHeader').removeClass('bg-dark').addClass('bg-success');
            $('#modalSubmitBtn')
                .html('<i class="bi bi-save"></i> Save')
                .data('mode', 'create');

            $('#contactModal').modal('show');

        } else {
            //  Edit mode
            $.ajax({
                url:  getUrl('get', id),
                type: 'GET',
                success: function (data) {

                    // Fill plain inputs
                    $('#contactId').val(data.id);
                    $('#id_name').val(data.name);
                    $('#id_phone_number').val(data.phone_number);
                    $('#id_email').val(data.email);

                    // Fill Select2 dropdown
                    // trigger('change') forces Select2 to update its UI
                    $('#id_contact_group').val(data.contact_group).trigger('change');
                    if (data.picture_url) {
                        showCurrentPicture(data.picture_url);
                    } else {
                        hideCurrentPicture();
                    }
                    $('#modalTitle').html('<i class="bi bi-pencil-square"></i> Edit Contact');
                    $('#modalHeader').removeClass('bg-success').addClass('bg-dark');
                    $('#modalSubmitBtn')
                        .html('<i class="bi bi-check-circle"></i> Update')
                        .data('mode', 'edit')
                        .data('id', id);

                    $('#contactModal').modal('show');
                },
                error: function () {
                    // SweetAlert2 for failed data fetch
                    showAlert(
                        'Failed!',
                        'Could not load contact data. Please try again.',
                        'error',
                        '#dc3545'
                    );
                }
            });
        }
    }

    //  ADD CONTACT BUTTON

    $('#addContactBtn').on('click', function () {
        openModal('create');
    });

    //  EDIT BUTTON
    //  Delegated because DataTable rows are dynamic

    $(document).on('click', '.btn-edit', function () {
        openModal('edit', $(this).data('id'));
    });

    //  MODAL SUBMIT — handles both Create and Update

    $('#modalSubmitBtn').on('click', function () {
        clearErrors();

        var mode = $(this).data('mode');  //mode reads whether the button is in create or edit state.
        var id   = $(this).data('id');
        var url  = (mode === 'create') ? URLS.create : getUrl('update', id);
        var cleared = $('#contactForm').data('picture-cleared');

        // FormData must be used so the file upload is included
        var formData = new FormData($('#contactForm')[0]);
        $.ajax({
            url:  url,
            type: 'POST',
            data: formData,
            // processData: false → do not convert FormData to a query string
            // contentType: false → let the browser set the multipart boundary
            processData: false,
            contentType: false,
            success: function (res) {
                $('#contactModal').modal('hide');
                refreshTable();

                if (mode === 'create') {
                    Swal.fire({
                        title: 'Created Successfully!',
                        text: res.message,
                        icon: 'success',
                        confirmButtonColor: '#198754',
                        timer: 2000,
                        showConfirmButton: false,
                        timerProgressBar: false,
                    });
                } 
                    else {                                                  
                        Swal.fire({
                            title: 'Updated Successfully!',
                            text: res.message,
                            icon: 'success',
                            confirmButtonColor: '#198754',
                            timer: 2000,
                            showConfirmButton: false,
                            timerProgressBar: false,
                        });
                    }
            },
            
            error: function (xhr) {
                var res = xhr.responseJSON;
                if (res && res.errors) {
                    // Display Django's field-level validation errors on the form
                    showErrors(res.errors);
                } else {
                    // SweetAlert2 for unexpected error
                    showAlert(
                        'Something went wrong!',
                        'Please try again.',
                        'error',
                        '#dc3545'
                    );
                }
            }
        });
    });

    //  DELETE — SweetAlert2 confirmation
    //  Delegated because rows are dynamic

    $(document).on('click', '.btn-delete', function () {
        var id   = $(this).data('id');
        var name = $(this).data('name');

        //  Step 1: Confirmation dialog 
        Swal.fire({
            title:              'Delete Contact?',
            html:               'Are you sure you want to delete ' +
                                '<strong>' + name + '</strong>?<br>' +
                                '<small class="text-muted">This action cannot be undone.</small>',
            icon:               'warning',
            showCancelButton:   true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor:  '#6c757d',
            confirmButtonText:  '<i class="bi bi-trash"></i> Yes, Delete',
            cancelButtonText:   'Cancel',
            reverseButtons:     true,
        }).then(function (result) {
            // Only proceed if the user clicked confirm
            if (!result.isConfirmed) return;
            $.ajax({
                url:  getUrl('delete', id),
                type: 'POST',
                success: function (res) {
                    refreshTable();

                    //  Step 2: Success dialog after delete ─
                    Swal.fire({
                        title:              'Deleted Successfully',
                        text:               res.message,
                        icon:               'success',       // green tick mark
                        confirmButtonColor: '#198754',
                        timer:              2000,
                        showConfirmButton:  false,
                        timerProgressBar:   true,
                    });
                },
                error: function () {

                    //  Step 2: Error dialog if delete fails ─
                    Swal.fire({
                        title:              'Delete Failed!',
                        text:               'Something went wrong. Please try again.',
                        icon:               'error',
                        confirmButtonColor: '#dc3545',
                    });
                }
            });
        });
    });

    //  RESET FORM when modal is fully closed

    $('#contactModal').on('hidden.bs.modal', function () {
        $('#contactForm')[0].reset();
        $('#contactId').val('');
        $('#contactForm').data('picture-cleared', false);
        hideCurrentPicture();
        clearErrors();

        // Reset Select2 dropdowns back to blank
        $('#contactForm select').each(function () {
            $(this).val(null).trigger('change');
        });
    });

});