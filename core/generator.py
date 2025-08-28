# D:\timetable_generator\timetable_project\core\generator.py
import random
from collections import defaultdict

# --- (Configuration constants are the same) ---
POPULATION_SIZE = 150
MAX_GENERATIONS = 250
MUTATION_RATE = 0.15
ELITISM_COUNT = 5

class TimetableGenerator:
    # --- (__init__ method is the same) ---
    def __init__(self, school_data):
        self.teachers = {t['id']: t for t in school_data.get('teachers', [])}
        self.subjects = {s['id']: s for s in school_data.get('subjects', [])}
        self.student_groups = {sg['id']: sg for sg in school_data.get('student_groups', [])}
        self.lessons = school_data.get('lessons', [])
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.periods_in_day = 8
        self.timeslots = [f"{day}-{period}" for day in self.days for period in range(1, self.periods_in_day + 1)]
        self.lesson_requirements = []
        for lesson_info in self.lessons:
            for _ in range(lesson_info['periods_per_week']):
                self.lesson_requirements.append({
                    "lesson_id": lesson_info['id'],
                    "subject_id": lesson_info['subject_id'],
                    "group_id": lesson_info['student_group_id'],
                    "is_double_period": lesson_info.get('is_double_period', False)
                })
        print("Generator initialized.")

    # --- (run_generation method is the same) ---
    def run_generation(self):
        print("Starting KVS-compliant timetable generation...")
        population = self.generate_initial_population()
        if not population:
            return {"status": "error", "message": "Could not generate initial population. Check lesson requirements."}

        for generation in range(MAX_GENERATIONS):
            print(f"--- Generation {generation + 1}/{MAX_GENERATIONS} ---")
            fitness_scores = [(self.calculate_fitness(timetable), timetable) for timetable in population]
            fitness_scores.sort(key=lambda x: x[0])
            best_score = fitness_scores[0][0]
            print(f"Best Score in Generation {generation + 1}: {best_score}")
            if best_score == 0:
                print("Perfect solution found!")
                best_timetable = fitness_scores[0][1]
                return self.format_timetable_for_frontend(best_timetable)
            
            parents = self.selection(fitness_scores)
            
            children = []
            while len(children) < POPULATION_SIZE - ELITISM_COUNT:
                parent1, parent2 = random.sample(parents, 2)
                child = self.crossover(parent1, parent2)
                if random.random() < MUTATION_RATE:
                    child = self.mutation(child)
                children.append(child)
            
            population = parents[:ELITISM_COUNT] + children

        print("Algorithm finished. Returning best found solution.")
        # This line was causing the crash
        valid_timetables = [t for t in population if t is not None]
        if not valid_timetables:
            return {"status": "error", "message": "Algorithm could not find a valid solution."}
        best_timetable = sorted([(self.calculate_fitness(t), t) for t in valid_timetables])[0][1]
        return self.format_timetable_for_frontend(best_timetable)

    # --- (generate_initial_population is the same) ---
    def generate_initial_population(self):
        population = []
        if not self.lesson_requirements or not self.teachers or not self.student_groups:
            return population # Return empty if no data to process
        for _ in range(POPULATION_SIZE):
            timetable = []
            for i, lesson_req in enumerate(self.lesson_requirements):
                lesson_assignment = {
                    "unique_id": i,
                    **lesson_req,
                    "teacher_id": random.choice(list(self.teachers.keys())),
                    "timeslot": random.choice(self.timeslots)
                }
                timetable.append(lesson_assignment)
            population.append(timetable)
        return population

    # --- (calculate_fitness is the same) ---
    def calculate_fitness(self, timetable):
        if timetable is None:
            return float('inf') # Return a very high penalty for invalid timetables
        # ... (rest of the fitness function is the same)
        penalty = 0
        teacher_slots = defaultdict(list)
        group_slots = defaultdict(list)
        for lesson in timetable:
            teacher_id = lesson['teacher_id']
            group_id = lesson['group_id']
            slot = lesson['timeslot']
            if slot in teacher_slots[teacher_id]: penalty += 1000
            teacher_slots[teacher_id].append(slot)
            if slot in group_slots[group_id]: penalty += 1000
            group_slots[group_id].append(slot)
        for teacher_id, slots in teacher_slots.items():
            max_periods = self.teachers[teacher_id].get('max_periods_per_week', 48)
            if len(slots) > max_periods: penalty += 500 * (len(slots) - max_periods)
        double_period_lessons = [l for l in timetable if l.get('is_double_period')]
        for dpl in double_period_lessons:
            day, period_str = dpl['timeslot'].split('-')
            period = int(period_str)
            is_paired = False
            for other_dpl in double_period_lessons:
                if dpl['unique_id'] != other_dpl['unique_id'] and dpl['lesson_id'] == other_dpl['lesson_id']:
                    other_day, other_period_str = other_dpl['timeslot'].split('-')
                    other_period = int(other_period_str)
                    if day == other_day and abs(period - other_period) == 1:
                        is_paired = True
                        break
            if not is_paired: penalty += 50
        return penalty

    # --- (selection method is the same) ---
    def selection(self, fitness_scores):
        elites = [fs[1] for fs in fitness_scores[:ELITISM_COUNT]]
        selected = []
        # Filter out any None values that might have slipped through
        valid_scores = [fs for fs in fitness_scores if fs[1] is not None]
        if not valid_scores: return elites # Return only elites if no other valid parents
        for _ in range(POPULATION_SIZE - ELITISM_COUNT):
            tournament = random.sample(valid_scores, min(10, len(valid_scores)))
            winner = min(tournament, key=lambda x: x[0])
            selected.append(winner[1])
        return elites + selected

    # --- CORRECTED Crossover Function ---
    def crossover(self, parent1, parent2):
        """ Combines two parents to create a child. """
        if not parent1 or not parent2:
            return parent1 or parent2 # Return a valid parent if one is invalid
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child # This now correctly returns the new child timetable

    # --- (mutation method is the same) ---
    def mutation(self, timetable):
        if not timetable: return timetable
        lesson_to_mutate = random.choice(timetable)
        lesson_to_swap_with = random.choice(timetable)
        lesson_to_mutate['timeslot'], lesson_to_swap_with['timeslot'] = lesson_to_swap_with['timeslot'], lesson_to_mutate['timeslot']
        return timetable

    # --- (format_timetable_for_frontend is the same) ---
    def format_timetable_for_frontend(self, timetable):
        all_schedules = []
        for group_id, group_info in self.student_groups.items():
            scheduled_lessons = []
            unique_lessons = {}
            for lesson in timetable:
                if lesson['group_id'] == group_id:
                    lesson_key = (lesson['timeslot'], lesson['group_id'])
                    if lesson_key not in unique_lessons:
                        subject = self.subjects[lesson['subject_id']]['subject_name']
                        teacher_obj = self.teachers[lesson['teacher_id']]
                        teacher = f"{teacher_obj['first_name']}"
                        day, period = lesson['timeslot'].split('-')
                        unique_lessons[lesson_key] = {
                            "id": lesson['unique_id'],
                            "subject": subject,
                            "teacher": teacher,
                            "day": day,
                            "timeslot": f"Period {period}"
                        }
            group_schedule = {
                "student_group_name": group_info['group_name'],
                "days": self.days,
                "timeslots": [f"Period {i}" for i in range(1, self.periods_in_day + 1)],
                "scheduled_lessons": list(unique_lessons.values())
            }
            all_schedules.append(group_schedule)
        return {
            "status": "complete",
            "message": "All timetables generated successfully.",
            "schedules": all_schedules
        }