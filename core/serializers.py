# core/serializers.py
from rest_framework import serializers
from .models import AlgorithmSettings
from .models import (
    Teacher,
    Subject,
    StudentGroup,
    TimeSlot,
    Lesson,
    ConstraintType,
    ConstraintInstance,
    ConstraintParameter
)

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ConstraintTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintType
        fields = '__all__'

class ConstraintInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintInstance
        fields = '__all__'

class ConstraintParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintParameter
        fields = '__all__'


class AlgorithmSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmSettings
        fields = ['key', 'value']