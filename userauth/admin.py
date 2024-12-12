from django.contrib import admin
from .models import Account, Librarian, AccountRequest
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class AccountsAdmin(ImportExportModelAdmin):
    list_display = ['lrn', 'fname', 'lname', 'birthday', 'age', 'email']

admin.site.register(Account, AccountsAdmin)  # Corrected: Account model and AccountsAdmin class
admin.site.register(Librarian)
admin.site.register(AccountRequest)
