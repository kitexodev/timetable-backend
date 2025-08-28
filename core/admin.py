# core/admin.py
from django.contrib import admin
from.models import (
    Teacher,
    Subject,
    StudentGroup,
    TimeSlot,
    Lesson,
    ConstraintType,
    ConstraintInstance,
    ConstraintParameter
)

# Register your models here to make them accessible in the Django admin panel.
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(StudentGroup)
admin.site.register(TimeSlot)
admin.site.register(Lesson)
admin.site.register(ConstraintType)
admin.site.register(ConstraintInstance)
admin.site.register(ConstraintParameter)