import settings
import initializers
import numpy as np
import logging

logger = logging.getLogger('aralap')

class AssistantAssignmentProblem:
    def __init__(self, constraints: tuple):
        logger.info('AssistantAssignmentProblem initialization started.')
        self.assistant_count = len(settings.ASSISTANT_PROGRAMS)
        self.course_count = len(settings.COURSES)
        self.unavailability_matrix = initializers.create_unavailability_matrix()
        self.courses_schedule_matrix = initializers.create_course_schedule_matrix()
        self.requests_matrix = initializers.create_requests_matrix()
        self.constraints = constraints
        logger.info('AssistantAssignmentProblem initialization finished.')
    
    def evaluate(self, X):
        X_to_be_used = np.array(X).reshape(self.assistant_count, self.course_count)
        # X_to_be_used = (X_to_be_used > 0.5).astype(int)

        cost = sum(constraint[1] * constraint[2](X_to_be_used, self.unavailability_matrix, self.courses_schedule_matrix, self.requests_matrix) for constraint in self.constraints)

        return cost,