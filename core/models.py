# core/models.py
from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50, help_text="e.g., 'PPRT', 'PRT', 'TGT', 'PGT'")
    max_periods_per_week = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.subject_name


class StudentGroup(models.Model):
    group_name = models.CharField(max_length=100, help_text="e.g., 'Grade 9A', 'AP History'")
    grade_level = models.CharField(max_length=20, help_text="e.g., 'Balvatika', '1', '12'")

    def __str__(self):
        return self.group_name

class TimeSlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(Teacher, help_text="Select one or more teachers for this lesson")
    periods_per_week = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.subject_name} for {self.student_group.group_name}"

# The following models are for the flexible constraint engine
class ConstraintType(models.Model):
    type_name = models.CharField(max_length=100, unique=True, help_text="Code name for the constraint, e.g., 'TEACHER_UNAVAILABLE'")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type_name

class ConstraintInstance(models.Model):
    LEVEL_CHOICES = [
        ('HARD', 'Hard'),
        ('SOFT', 'Soft'),
    ]
    constraint_type = models.ForeignKey(ConstraintType, on_delete=models.CASCADE)
    constraint_level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    weight = models.IntegerField(default=0, help_text="Penalty weight if the constraint is 'Soft'")

    def __str__(self):
        return f"{self.constraint_type.type_name} ({self.constraint_level})"

class ConstraintParameter(models.Model):
    instance = models.ForeignKey(ConstraintInstance, on_delete=models.CASCADE, related_name='parameters')
    parameter_key = models.CharField(max_length=50, help_text="e.g., 'teacher_id', 'timeslot_id'")
    parameter_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.instance}: {self.parameter_key} = {self.parameter_value}"