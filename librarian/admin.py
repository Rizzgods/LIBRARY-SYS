from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from .models import Books, Category, BorrowRequest,ApprovedRequest,DeclinedRequest, SubCategory, Out, ReturnLog, SubSection
# Register your models here.
class SubsectionAdmin(ImportExportModelAdmin):
    list_display = ['sub_category', 'name', 'code']


admin.site.register(Books)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubSection, SubsectionAdmin)
admin.site.register(BorrowRequest)
admin.site.register(ApprovedRequest)
admin.site.register(DeclinedRequest)
admin.site.register(Out)
admin.site.register(ReturnLog)

