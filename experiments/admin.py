from django.contrib import admin
from models import *

class SubjectAdmin(admin.ModelAdmin):
    exclude=('active', 'fail_status')

# Register your models here.
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Phase)
admin.site.register(Symbol)
admin.site.register(SingleSet)
admin.site.register(Group)
