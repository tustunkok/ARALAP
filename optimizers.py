import numpy as np
import logging
import settings

logger = logging.getLogger('araap')

def greedy(problem, iter_count=50, result_matrix=None, exclude_courses=list()):
    assistant_count = len(settings.assistant_programs)
    course_count = len(settings.courses)
    if result_matrix is None:
        logger.info("No default result matrix is provided. Creating empty one.")
        result_matrix = np.zeros((assistant_count, course_count), dtype=int)
        result_test_matrix = np.zeros((assistant_count, course_count), dtype=int)
    else:
        logger.info("Default result matrix is provided. Using it.")
        logger.info("Excluding courses %s", exclude_courses)
        result_test_matrix = np.copy(result_matrix)
    
    for course in range(course_count):
        asst_idx = int(np.random.rand(1)[0] * assistant_count)
        if course in exclude_courses:
            continue
        result_matrix[asst_idx, course] = 1
        result_test_matrix[asst_idx, course] = 1
    
    progress = True
    previous_cost = np.inf
    iter_idx = 0
    while progress and iter_idx < iter_count:
        min_loss_value = np.inf
        for assistant1 in range(assistant_count - 1):
            for course in range(course_count):
                if course in exclude_courses:
                    continue
                for assistant2 in range(assistant1 + 1, assistant_count):
                    result_test_matrix[assistant1, course], result_test_matrix[assistant2, course] = \
                        result_test_matrix[assistant2, course], result_test_matrix[assistant1, course]

                    temp_loss = problem.evaluate(result_test_matrix, verbose=False)
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