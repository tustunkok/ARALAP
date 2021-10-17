import numpy as np
import initializers
import settings
import logging

logger = logging.getLogger('araap')

class AssistantAssignmentProblem:
    def __init__(self):
        logger.info('AssistantAssignmentProblem initialization started.')
        self.assistant_count = len(settings.assistant_programs)
        self.course_count = len(settings.courses)
        self.distinct_course_count = len(set([course["id"].split("-")[0] for course in settings.courses]))
        self.unavailability_matrix = initializers.create_unavailability_matrix()
        self.courses_schedule_matrix = initializers.create_course_schedule_matrix()
        self.requests_matrix = initializers.create_requests_matrix()
        logger.info('AssistantAssignmentProblem initialization finished.')

    def hard_constraint_1(self, X):
        total = 0
        for asst_id, _ in enumerate(settings.assistant_programs):
            assigned_courses = np.array(settings.courses)[X[asst_id].astype(bool)]

            for i in range(len(assigned_courses) - 1):
                for j in range(i + 1, len(assigned_courses)):
                    if assigned_courses[i]["day"] == assigned_courses[j]["day"]:
                        total += len(list(set(assigned_courses[i]["periods"]) & set(assigned_courses[j]["periods"]))) * 500

        return total if total != np.nan else np.inf


    def hard_constraint_2(self, X):
        return np.sum(np.sum(X, axis=0) > 1) * 500


    def soft_constraint_1(self, X):
        final_result = 0
        worst_result = 0
        
        for asst_id, _ in enumerate(settings.assistant_programs):
            resultant_matrix = self.unavailability_matrix[asst_id].copy()

            for course_schedule in self.courses_schedule_matrix[X[asst_id].astype(bool)]:
                resultant_matrix += course_schedule

            final_result += np.sum(resultant_matrix > 1)
            worst_result += len(self.courses_schedule_matrix[X[asst_id].astype(bool)])
        
        return final_result / worst_result


    def soft_constraint_2(self, X):
        final_result = 0
        worst_result = 0

        for asst_id, _ in enumerate(settings.assistant_programs):
            course_sum = 0
            assigned_courses = np.array(settings.courses)[X[asst_id].astype(bool)]
            for assigned_course in assigned_courses:
                course_sum += self.requests_matrix[asst_id, initializers.get_course_index(assigned_course["id"].split("-")[0])]

            final_result += np.abs(course_sum - len(assigned_courses))
            worst_result += len(assigned_courses)
        
        return final_result / worst_result


    def soft_constraint_3(self, X):
        return np.sum(np.sum(X, axis=0) == 0) / self.course_count


    def soft_constraint_4(self, X):
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
