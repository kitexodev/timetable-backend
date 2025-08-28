# D:\timetable_generator\timetable_project\core\views.py
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.http import HttpResponse
import openpyxl
import json
import io

from .models import (
    Teacher, Subject, StudentGroup, TimeSlot, Lesson,
    ConstraintType, ConstraintInstance, ConstraintParameter
)
from .serializers import (
    TeacherSerializer, SubjectSerializer, StudentGroupSerializer,
    TimeSlotSerializer, LessonSerializer, ConstraintTypeSerializer,
    ConstraintInstanceSerializer, ConstraintParameterSerializer
)
from .generator import TimetableGenerator

# --- Data Management Views (RoomViewSet removed) ---
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class StudentGroupViewSet(viewsets.ModelViewSet):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer

# ... other viewsets
class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class ConstraintTypeViewSet(viewsets.ModelViewSet):
    queryset = ConstraintType.objects.all()
    serializer_class = ConstraintTypeSerializer

class ConstraintInstanceViewSet(viewsets.ModelViewSet):
    queryset = ConstraintInstance.objects.all()
    serializer_class = ConstraintInstanceSerializer

class ConstraintParameterViewSet(viewsets.ModelViewSet):
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

# --- Core Functionality Views ---
class GenerateTimetableView(APIView):
    def post(self, request, *args, **kwargs):
        school_data = {
            "teachers": list(Teacher.objects.values()),
            "subjects": list(Subject.objects.values()),
            # "rooms" removed
            "student_groups": list(StudentGroup.objects.values()),
            "timeslots": list(TimeSlot.objects.values()),
            "lessons": list(Lesson.objects.values()),
        }
        generator = TimetableGenerator(school_data)
        result = generator.run_generation()
        return Response(result)

class ExportTimetableView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            schedule_data = json.loads(request.body).get('schedule')
            if not schedule_data:
                return HttpResponse("Invalid data", status=400)

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = schedule_data.get('student_group_name', 'Timetable').replace(":", "")

            headers = ['Time'] + schedule_data.get('days', [])
            ws.append(headers)

            grid = {}
            for slot in schedule_data.get('timeslots', []):
                grid[slot] = {day: "" for day in schedule_data.get('days', [])}

            for lesson in schedule_data.get('scheduled_lessons', []):
                cell_content = f"{lesson['subject']}\n{lesson['teacher']}"
                grid[lesson['timeslot']][lesson['day']] = cell_content

            for slot in schedule_data.get('timeslots', []):
                row_data = [slot] + [grid[slot][day] for day in schedule_data.get('days', [])]
                ws.append(row_data)

            # Use an in-memory buffer for a reliable save
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = schedule_data.get('student_group_name', 'timetable').replace(" ", "_")
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            return response
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
class ValidateMoveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            all_schedules = data.get('all_schedules')
            moved_lesson_id = data.get('moved_lesson_id')
            new_day = data.get('new_day')
            new_timeslot = data.get('new_timeslot')

            if not all_schedules or not moved_lesson_id or not new_day or not new_timeslot:
                return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)

            moved_lesson = None
            for schedule in all_schedules:
                for lesson in schedule.get('scheduled_lessons', []):
                    if lesson.get('id') == moved_lesson_id:
                        moved_lesson = lesson
                        break
                if moved_lesson:
                    break
            
            if not moved_lesson:
                 return Response({"valid": False, "reason": "Moved lesson not found."})

            teacher_name = moved_lesson.get('teacher')
            target_timeslot_full = f"{new_day}-{new_timeslot}"

            for schedule in all_schedules:
                for lesson in schedule.get('scheduled_lessons', []):
                    if lesson.get('id') == moved_lesson_id:
                        continue
                    
                    lesson_timeslot_full = f"{lesson.get('day')}-{lesson.get('timeslot')}"
                    if lesson.get('teacher') == teacher_name and lesson_timeslot_full == target_timeslot_full:
                        return Response({
                            "valid": False,
                            "reason": f"Teacher {teacher_name} is already busy.",
                            "conflicting_lesson_id": lesson.get('id') # Return the conflicting lesson's ID
                        })

            return Response({"valid": True})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    """
    A custom ViewSet for handling AlgorithmSettings by their key.
    """
    def list(self, request):
        """ Handles GET requests to /api/settings/ """
        queryset = AlgorithmSettings.objects.all()
        serializer = AlgorithmSettingsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ Handles GET requests to /api/settings/<key>/ """
        try:
            setting = AlgorithmSettings.objects.get(pk=pk)
            serializer = AlgorithmSettingsSerializer(setting)
            return Response(serializer.data)
        except AlgorithmSettings.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Handles PUT requests to /api/settings/<key>/.
        This will create the setting if it does not exist, or update it if it does.
        """
        try:
            setting, created = AlgorithmSettings.objects.update_or_create(
                pk=pk,
                defaults={'value': request.data.get('value')}
            )
            serializer = AlgorithmSettingsSerializer(setting)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)