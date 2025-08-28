# core/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from.views import (
    GenerateTimetableView,
    ExportTimetableView,
    TeacherViewSet,
    SubjectViewSet,
    StudentGroupViewSet,
    TimeSlotViewSet,
    LessonViewSet,
    ConstraintTypeViewSet,
    ConstraintInstanceViewSet,
    ConstraintParameterViewSet,
    ValidateMoveView,
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'student-groups', StudentGroupViewSet)
router.register(r'timeslots', TimeSlotViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'constraint-types', ConstraintTypeViewSet)
router.register(r'constraint-instances', ConstraintInstanceViewSet)
router.register(r'constraint-parameters', ConstraintParameterViewSet)

urlpatterns = router.urls

# This line adds the custom 'generate' endpoint
urlpatterns += [
    path('generate/', GenerateTimetableView.as_view(), name='generate-timetable'),
    path('export/', ExportTimetableView.as_view(), name='export-timetable'),
    path('validate-move/', ValidateMoveView.as_view(), name='validate-move'),
]