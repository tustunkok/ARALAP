import numpy as np
import logging
import settings

logger = logging.getLogger('aralap')


def swap(problem, result_matrix, iter_count, assistant_count, course_count, exclude_courses, exclude_assistants):
    result_test_matrix = np.copy(result_matrix)
    progress = True
    previous_cost = np.inf
    iter_idx = 0
    while progress and iter_idx < iter_count:
        min_loss_value = np.inf
        for assistant1 in range(assistant_count - 1):
            if assistant1 in exclude_assistants:
                continue
            for course in range(course_count):
                if course in exclude_courses:
                    continue
                for assistant2 in range(assistant1 + 1, assistant_count):
                    if assistant2 in exclude_assistants:
                        continue
                    result_test_matrix[assistant1, course], result_test_matrix[assistant2, course] = \
                        result_test_matrix[assistant2, course], result_test_matrix[assistant1, course]

                    temp_loss = problem.evaluate(result_test_matrix)
                    if temp_loss < min_loss_value:
                        min_loss_assistant1_idx = assistant1
                        min_loss_assistant2_idx = assistant2
                        min_loss_value = temp_loss
                        min_loss_course = course

                    result_test_matrix = np.copy(result_matrix)

        result_matrix[min_loss_assistant1_idx, min_loss_course], result_matrix[min_loss_assistant2_idx, min_loss_course] = \
                result_matrix[min_loss_assistant2_idx, min_loss_course], result_matrix[min_loss_assistant1_idx, min_loss_course]
        result_test_matrix = np.copy(result_matrix)
        
        print(f"EPOCH: {iter_idx}\tCOST: {min_loss_value:.4f}")
        # logger.info(f"EPOCH: {iter_idx}\tCOST: {min_loss_value:.4f}")
        iter_idx += 1
        
        if previous_cost == min_loss_value:
            progress = False
        previous_cost = min_loss_value
    return result_matrix


def greedy_wo_randomization(problem, iter_count=50, result_matrix=None, exclude_courses=[], exclude_assistants=[]):
    assistant_count = len(settings.ASSISTANT_PROGRAMS)
    course_count = len(settings.COURSES)
    result_matrix = np.zeros((assistant_count, course_count), dtype=int)
    result_test_matrix = np.zeros((assistant_count, course_count), dtype=int)

    for course in range(course_count):
        initial_loss = np.inf
        winning_asst = -1
        for asst_idx in range(assistant_count):
            result_test_matrix[asst_idx, course] = 1
            loss = problem.evaluate(result_test_matrix, verbose=False)
            if loss < initial_loss:
                result_test_matrix = np.copy(result_matrix)
                initial_loss = loss
                winning_asst = asst_idx
        
        result_matrix[winning_asst, course] = 1
    
    return swap(problem, result_matrix, iter_count, assistant_count, course_count, exclude_courses, exclude_assistants)



def greedy(problem, iter_count=50, result_matrix=None, exclude_courses=[], exclude_assistants=[]):
    assistant_count = len(settings.ASSISTANT_PROGRAMS)
    course_count = len(settings.COURSES)
    if result_matrix is None:
        logger.info("No default result matrix is provided. Creating empty one.")
        result_matrix = np.zeros((assistant_count, course_count), dtype=int)
    else:
        logger.info("Default result matrix is provided. Using it.")
        logger.info("Excluding courses %s", exclude_courses)
    
    for course in range(course_count):
        asst_idx = int(np.random.rand(1)[0] * assistant_count)
        while asst_idx in exclude_assistants:
            asst_idx = int(np.random.rand(1)[0] * assistant_count)
        if course in exclude_courses:
            continue
        result_matrix[asst_idx, course] = 1
    
    return swap(problem, result_matrix, iter_count, assistant_count, course_count, exclude_courses, exclude_assistants)
