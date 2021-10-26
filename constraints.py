import itertools
import numpy as np
from numpy.lib.function_base import diff
import initializers
import settings
import logging

logger = logging.getLogger('araap')

class AssistantAssignmentProblem:
    def __init__(self):
        logger.info('AssistantAssignmentProblem initialization started.')
        self.assistant_count = len(settings.ASSISTANT_PROGRAMS)
        self.course_count = len(settings.COURSES)
        self.distinct_course_count = len(set([course["id"].split("-")[0] for course in settings.COURSES]))
        self.unavailability_matrix = initializers.create_unavailability_matrix()
        self.courses_schedule_matrix = initializers.create_course_schedule_matrix()
        self.requests_matrix = initializers.create_requests_matrix()
        logger.info('AssistantAssignmentProblem initialization finished.')
    
    def evaluate(self, X, verbose=False):
        X_to_be_used = X.reshape(self.assistant_count, self.course_count)
        costs = {
            "Hard Constraint 1": 100 * self.hard_constraint_1(X_to_be_used),
            "Hard Constraint 2": 100 * self.hard_constraint_2(X_to_be_used),
            "Soft Constraint 1": 40.0 * self.soft_constraint_1(X_to_be_used),
            "Soft Constraint 2": 15.0 * self.soft_constraint_2(X_to_be_used),
            "Soft Constraint 3": 10.0 * self.soft_constraint_3(X_to_be_used),
            "Soft Constraint 4": 20.0 * self.soft_constraint_4(X_to_be_used),
            "Soft Constraint 5": 10.0 * self.soft_constraint_5(X_to_be_used),
            "Soft Constraint 6": 5.0 * self.soft_constraint_6(X_to_be_used)
        }

        if verbose:
            result = str()
            for k, v in costs.items():
                result += f"{k}: {v}\n"
            return result
        
        
        return np.sum([v for _, v in costs.items()])

    def hard_constraint_1(self, X):
        total = 0
        for asst_id, _ in enumerate(settings.ASSISTANT_PROGRAMS):
            assigned_courses = np.array(settings.COURSES)[X[asst_id].astype(bool)]

            for i in range(len(assigned_courses) - 1):
                for j in range(i + 1, len(assigned_courses)):
                    if assigned_courses[i]["day"] == assigned_courses[j]["day"]:
                        total += len(list(set(assigned_courses[i]["periods"]) & set(assigned_courses[j]["periods"]))) * 500

        return total if total != np.nan else np.inf


    def hard_constraint_2(self, X):
        return np.sum(np.sum(X, axis=0) > 1) * 500


    def soft_constraint_1(self, X):
        """Labs should not be assigned to unavailable slots."""
        final_result = 0
        worst_result = 0
        
        for asst_id, _ in enumerate(settings.ASSISTANT_PROGRAMS):
            resultant_matrix = self.unavailability_matrix[asst_id].copy()

            for course_schedule in self.courses_schedule_matrix[X[asst_id].astype(bool)]:
                resultant_matrix += course_schedule

            final_result += np.sum(resultant_matrix > 1)
            worst_result += len(self.courses_schedule_matrix[X[asst_id].astype(bool)])
        
        return final_result / worst_result


    def soft_constraint_2(self, X):
        """Labs should be assigned according to the assistant requests."""
        final_result = 0
        worst_result = 0

        for asst_id, _ in enumerate(settings.ASSISTANT_PROGRAMS):
            course_sum = 0
            assigned_courses = np.array(settings.COURSES)[X[asst_id].astype(bool)]
            for assigned_course in assigned_courses:
                course_sum += self.requests_matrix[asst_id, initializers.get_course_index(assigned_course["id"].split("-")[0])]

            final_result += np.abs(course_sum - len(assigned_courses))
            worst_result += len(assigned_courses)
        
        return final_result / worst_result


    def soft_constraint_3(self, X):
        """All labs should be assigned to assistants."""
        return np.sum(np.sum(X, axis=0) == 0) / self.course_count


    def soft_constraint_4(self, X):
        """All assistant loads should be equal."""
        assistant_loads = list()
        for assistant_idx in range(self.assistant_count):
            assistant_total = 0
            for course_idx in range(self.course_count):
                if X[assistant_idx, course_idx] == 1:
                    assistant_total += np.sum(self.courses_schedule_matrix[course_idx])
            assistant_loads.append(assistant_total)
        
        assistant_loads = np.array(assistant_loads)
        load_mean = np.mean(assistant_loads)
        return np.var(assistant_loads) / load_mean
    

    def soft_constraint_5(self, X):
        """Same type of labs should be assigned."""
        all_stds = list()
        for asst_id, _ in enumerate(settings.ASSISTANT_PROGRAMS):
            assigned_courses = np.array(settings.COURSES)[X[asst_id].astype(bool)]
            raw_assigned_courses = list()
            for assigned_course in assigned_courses:
                raw_assigned_courses.append(initializers.get_course_index(assigned_course["id"].split("-")[0]))
            all_stds.append(np.var(raw_assigned_courses) / np.mean(raw_assigned_courses))
        return np.sum(all_stds) / len(settings.ASSISTANT_PROGRAMS)
    

    def soft_constraint_6(self, X):
        """Consecutive laboratory hours should be assigned."""
        all_assistants_non_periodic_hours = 0
        for asst_id, _ in enumerate(settings.ASSISTANT_PROGRAMS):
            assigned_courses = np.array(settings.COURSES)[X[asst_id].astype(bool)]
            different_days = set([course['day'] for course in assigned_courses])
            total_non_periodic_hours = 0
            for different_day in different_days:
                periods_in_same_day = [course['periods'] for course in assigned_courses if course['day'] == different_day]
                periods = list(itertools.chain.from_iterable(periods_in_same_day))
                period_diffs = np.diff(periods)
                cost = np.sum(period_diffs[period_diffs > 1]) / 8
                total_non_periodic_hours += cost
            if len(different_days) == 0:
                continue
            all_assistants_non_periodic_hours += total_non_periodic_hours / len(different_days)
        return all_assistants_non_periodic_hours / len(settings.ASSISTANT_PROGRAMS)

