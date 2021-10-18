import numpy as np
import settings
import logging
import initializers
import json

logger = logging.getLogger('araap')

def get_course_index(course_name):
    course_names = np.array(sorted(list(set([course["id"].split("-")[0] for course in settings.courses]))))
    return None if len(np.where(course_names == course_name)[0]) == 0 else np.where(course_names == course_name)[0][0]


def get_course_index_from_all(course_name):
    course_names = np.array([course["id"] for course in settings.courses])
    return None if len(np.where(course_names == course_name)[0]) == 0 else np.where(course_names == course_name)[0][0]


def get_assistant_index(assistant_name):
    assistant_names = np.array([assistant["name"] for assistant in settings.assistant_programs])
    return None if len(np.where(assistant_names == assistant_name)[0]) == 0 else np.where(assistant_names == assistant_name)[0][0]


def create_course_schedule_matrix():
    # First axis shows the course, second axis shows the day, third axis shows the period and the value shows the course is here or not.
    # 1 is period occupied, 0 is period empty

    course_count = len(settings.courses)
    courses_schedule_matrix = np.zeros((course_count, settings.DAY_COUNT, settings.PERIOD_COUNT), dtype=int)

    for idx, course in enumerate(settings.courses):
        for period in course["periods"]:
            courses_schedule_matrix[idx, settings.DAY_INDICES[course["day"]], period] = 1
    
    logger.debug("Course schedule matrix:\n%s", courses_schedule_matrix)

    return courses_schedule_matrix


def create_unavailability_matrix():
    # First axis shows the assistant, second axis shows the day, third axis shows the period and the value shows the availability.
    # 1 is unavailable, 0 is available

    assistant_count = len(settings.assistant_programs)
    unavailability_matrix = np.zeros((assistant_count, settings.DAY_COUNT, settings.PERIOD_COUNT), dtype=int)

    for idx, assistant in enumerate(settings.assistant_programs):
        for unavailability in assistant["unavailabilities"]:
            for period in unavailability["periods"]:
                unavailability_matrix[idx, settings.DAY_INDICES[unavailability["day"]], period] = 1

    logger.debug("Unavailability matrix:\n%s", unavailability_matrix)
    return unavailability_matrix


def create_requests_matrix():
    # First axis shows the assistant, second axis shows the course and the value shows the if it is requested.
    # 1 is requested, 0 is not

    assistant_count = len(settings.assistant_programs)
    distinct_course_count = len(set([course["id"].split("-")[0] for course in settings.courses]))
    requests_matrix = np.zeros((assistant_count, distinct_course_count), dtype=int)

    for idx, assistant in enumerate(settings.assistant_programs):
        for requested_course in assistant["requested_course_ids"]:
            requests_matrix[idx, get_course_index(requested_course)] = 1

    logger.debug("Request matrix:\n%s", requests_matrix)
    return requests_matrix


def create_result_matrix(existing_program):
    existing_prog = json.load(existing_program)
        
    result_matrix = np.zeros((len(settings.assistant_programs), len(settings.courses)), dtype=int)
    assigned_courses = list()
    for prog in existing_prog:
        asst_idx = initializers.get_assistant_index(prog['name'])
        for assigned_lab in prog['assigned_labs']:
            course_idx = initializers.get_course_index_from_all(assigned_lab['id'])
            result_matrix[asst_idx, course_idx] = 1
            assigned_courses.append(course_idx)
    
    return (result_matrix, assigned_courses)