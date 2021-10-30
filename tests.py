import unittest
import settings
import initializers
import loaders
import constraints
import numpy as np

class ConstraintsTestCase(unittest.TestCase):
    
    def test_hard_constraint_1(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-hc1")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

        result_matrix[0, 0] = 1
        result_matrix[0, 2] = 1
        result_matrix[1, 1] = 1

        result_matrix1 = np.copy(result_matrix)
        result_matrix1[0, 2] = 0
        result_matrix1[0, 1] = 1
        result_matrix1[2, 3] = 1
        result_matrix1[2, 2] = 1

        self.assertEqual(constraints.hard_constraint_1(result_matrix), 1000)
        self.assertEqual(constraints.hard_constraint_1(result_matrix1), 500)
    
    def test_hard_constraint_2(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-hc1")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

        result_matrix[0, 3] = 1
        result_matrix[1, 3] = 1
        result_matrix1 = np.copy(result_matrix)
        result_matrix2 = np.copy(result_matrix)
        result_matrix1[1, 3] = 0
        result_matrix1[1, 2] = 1
        result_matrix2 = np.copy(result_matrix)
        result_matrix2[2, 2] = 1
        result_matrix2[1, 2] = 1

        self.assertEqual(constraints.hard_constraint_2(result_matrix), 500)
        self.assertEqual(constraints.hard_constraint_2(result_matrix1), 0)
        self.assertEqual(constraints.hard_constraint_2(result_matrix2), 1000)
    
    def test_soft_constraint_1(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc1")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        unavailability_matrix = initializers.create_unavailability_matrix()
        courses_schedule_matrix = initializers.create_course_schedule_matrix()
        requests_matrix = initializers.create_requests_matrix()
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)
        result_matrix1 = np.copy(result_matrix)

        result_matrix[initializers.get_assistant_index('John Doe'), 1] = 1
        result_matrix[initializers.get_assistant_index('Jane Doe'), 3] = 1
        result_matrix[initializers.get_assistant_index('Maudie Bradford'), 2] = 1
        result_matrix1[initializers.get_assistant_index('John Doe'), 1] = 1
        result_matrix1[initializers.get_assistant_index('Jane Doe'), 2] = 1

        self.assertEqual(constraints.soft_constraint_1(result_matrix, unavailability_matrix, courses_schedule_matrix, requests_matrix), 1)
        self.assertEqual(constraints.soft_constraint_1(result_matrix1, unavailability_matrix, courses_schedule_matrix, requests_matrix), 0.5)
    
    def test_soft_constraint_2(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc2")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        requests_matrix = initializers.create_requests_matrix()
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

        result_matrix[initializers.get_assistant_index('Maudie Bradford'), 0] = 1
        result_matrix[initializers.get_assistant_index('Jane Doe'), 1] = 1

        self.assertEqual(constraints.soft_constraint_2(result_matrix, None, None, requests_matrix), 0.5)
    
    def test_soft_constraint_3(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc2")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

        result_matrix[initializers.get_assistant_index('Maudie Bradford'), 0] = 1

        result_matrix1 = np.copy(result_matrix)
        result_matrix1[initializers.get_assistant_index('John Doe'), 1] = 1
        result_matrix1[initializers.get_assistant_index('Jane Doe'), 2] = 1
        result_matrix1[initializers.get_assistant_index('Jane Doe'), 3] = 1

        self.assertEqual(constraints.soft_constraint_3(result_matrix), 0.75)
        self.assertEqual(constraints.soft_constraint_3(result_matrix1), 0)
    
    def test_soft_constraint_4(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc1")
        with open('./test-jsons/test-courses-hc1.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        courses_schedule_matrix = initializers.create_course_schedule_matrix()
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

        result_matrix[initializers.get_assistant_index('John Doe'), 1] = 1
        result_matrix[initializers.get_assistant_index('Jane Doe'), 2] = 1
        result_matrix[initializers.get_assistant_index('Maudie Bradford'), 3] = 1

        result_matrix1 = np.copy(result_matrix)
        result_matrix1[initializers.get_assistant_index('Jane Doe'), 0] = 1

        self.assertEqual(constraints.soft_constraint_4(result_matrix, None, courses_schedule_matrix, None), 0)
        self.assertTrue(constraints.soft_constraint_4(result_matrix1, None, courses_schedule_matrix, None) > 0)
        self.assertTrue(constraints.soft_constraint_4(result_matrix1, None, courses_schedule_matrix, None) < 1)
    
    def test_soft_constraint_5(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc2")
        with open('./test-jsons/test-courses-sc5.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)
        result_matrix1 = np.copy(result_matrix)

        result_matrix[initializers.get_assistant_index('John Doe'), 0] = 1
        result_matrix[initializers.get_assistant_index('John Doe'), 1] = 1
        result_matrix[initializers.get_assistant_index('Jane Doe'), 2] = 1
        result_matrix[initializers.get_assistant_index('Maudie Bradford'), 3] = 1

        result_matrix1[initializers.get_assistant_index('John Doe'), 0] = 1
        result_matrix1[initializers.get_assistant_index('John Doe'), 2] = 1
        result_matrix1[initializers.get_assistant_index('Jane Doe'), 1] = 1
        result_matrix1[initializers.get_assistant_index('Maudie Bradford'), 3] = 1

        self.assertEqual(constraints.soft_constraint_5(result_matrix), 0)
        self.assertTrue(constraints.soft_constraint_5(result_matrix1) > 0)
        self.assertTrue(constraints.soft_constraint_5(result_matrix1) < 1)
    
    def test_soft_constraint_6(self):
        settings.ASSISTANT_PROGRAMS = loaders.load_programs('./test-programs/', test_case_pattern="-sc2")
        with open('./test-jsons/test-courses-sc5.json', 'r') as courses:
            settings.COURSES = loaders.load_courses(courses)
        result_matrix = np.zeros((len(settings.ASSISTANT_PROGRAMS), len(settings.COURSES)), dtype=int)

