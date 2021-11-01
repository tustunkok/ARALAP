import numpy as np
import logging
import settings
import initializers
import constraints
from problems import AssistantAssignmentProblem
from deap import base, creator, tools, algorithms
import multiprocessing

creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
creator.create('Individual', list, fitness=creator.FitnessMin)

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
            for assistant2 in range(assistant1 + 1, assistant_count):
                if assistant2 in exclude_assistants:
                    continue
                for course in range(course_count):
                    if course in exclude_courses:
                        continue
                    result_test_matrix[assistant1, course], result_test_matrix[assistant2, course] = \
                        result_test_matrix[assistant2, course], result_test_matrix[assistant1, course]

                    temp_loss, *others = problem.evaluate(result_test_matrix)
                    if temp_loss < min_loss_value:
                        min_loss_assistant1_idx = assistant1
                        min_loss_assistant2_idx = assistant2
                        min_loss_value = temp_loss
                        min_loss_course = course

                    result_test_matrix = np.copy(result_matrix)

        result_matrix[min_loss_assistant1_idx, min_loss_course], result_matrix[min_loss_assistant2_idx, min_loss_course] = \
                result_matrix[min_loss_assistant2_idx, min_loss_course], result_matrix[min_loss_assistant1_idx, min_loss_course]
        result_test_matrix = np.copy(result_matrix)
        
        logger.info(f"EPOCH: {iter_idx}/{iter_count}\tCOST: {min_loss_value:.4f}")
        iter_idx += 1
        
        if previous_cost == min_loss_value:
            progress = False
        previous_cost = min_loss_value
    
    logger.info("Starting substitutions.")
    for assistant1 in range(assistant_count - 1):
        assigned_courses1 = np.array(settings.COURSES)[result_matrix[assistant1].astype(bool)]
        if assistant1 in exclude_assistants:
            continue
        for assistant2 in range(assistant1 + 1, assistant_count):
            assigned_courses2 = np.array(settings.COURSES)[result_matrix[assistant2].astype(bool)]
            if assistant2 in exclude_assistants:
                continue
            for assigned_course1 in assigned_courses1:
                assigned_course1_idx = initializers.get_course_index(assigned_course1["id"].split("-")[0])
                for assigned_course2 in assigned_courses2:
                    assigned_course2_idx = initializers.get_course_index(assigned_course2["id"].split("-")[0])
                    result_test_matrix[assistant1, assigned_course1_idx], result_test_matrix[assistant2, assigned_course2_idx] = \
                    result_test_matrix[assistant2, assigned_course2_idx], result_test_matrix[assistant1, assigned_course1_idx]

                    temp_loss, *others = problem.evaluate(result_test_matrix)
                    prev_loss_value, *others = problem.evaluate(result_matrix)
                    logger.debug(f"Checking {assistant1} and {assistant2} for {assigned_course1['id']} and {assigned_course2['id']}")
                    logger.debug(f"New loss: {temp_loss} - Prev. loss: {prev_loss_value}")
                    if temp_loss < prev_loss_value:
                        result_matrix[assistant1, assigned_course1_idx], result_matrix[assistant2, assigned_course2_idx] = \
                        result_matrix[assistant2, assigned_course2_idx], result_matrix[assistant1, assigned_course1_idx]
                        logger.info(f"After EPOCH: {iter_idx}\tCOST: {temp_loss:.4f}")
                    else:
                        result_test_matrix = np.copy(result_matrix)

    logger.info("Substitutions are finished.")
    return result_matrix


def greedy_greedy_init(problem, iter_count=50, result_matrix=None, exclude_courses=[], exclude_assistants=[]):
    assistant_count = len(settings.ASSISTANT_PROGRAMS)
    course_count = len(settings.COURSES)

    if result_matrix is None:
        logger.info("No default result matrix is provided. Creating empty one.")
        result_matrix = np.zeros((assistant_count, course_count), dtype=int)
    else:
        logger.info("Default result matrix is provided. Using it.")
        logger.info("Excluding courses %s", exclude_courses)

    for course in range(course_count):
        if course in exclude_courses:
            continue
        while True:
            asst_idx = int(np.random.rand(1)[0] * assistant_count)
            while asst_idx in exclude_assistants:
                asst_idx = int(np.random.rand(1)[0] * assistant_count)
            
            result_matrix[asst_idx, course] = 1
            if constraints.hard_constraint_1(result_matrix) < 100 and constraints.hard_constraint_2(result_matrix) < 100:
                break
            else:
                result_matrix[asst_idx, course] = 0
    
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


def init_individual(icls):
    assistant_count = len(settings.ASSISTANT_PROGRAMS)
    course_count = len(settings.COURSES)
    result_matrix = np.zeros((assistant_count, course_count), dtype=int)
    for course in range(course_count):
        while True:
            asst_idx = int(np.random.rand(1)[0] * assistant_count)
            result_matrix[asst_idx, course] = 1
            if constraints.hard_constraint_1(result_matrix) < 100 and constraints.hard_constraint_2(result_matrix) < 100:
                break
            else:
                result_matrix[asst_idx, course] = 0
    return icls(result_matrix.flatten().tolist())


def ga_optimizer(problem: AssistantAssignmentProblem, iter_count=100, **kwargs):
    assistant_count = len(settings.ASSISTANT_PROGRAMS)
    course_count = len(settings.COURSES)
    pool = multiprocessing.Pool()

    toolbox = base.Toolbox()

    toolbox.register("map", pool.map)
    toolbox.register('individual', init_individual, creator.Individual)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    toolbox.register('mate', tools.cxTwoPoint)
    toolbox.register('mutate', tools.mutFlipBit, indpb=0.05)
    toolbox.register('select', tools.selTournament, tournsize=3)
    toolbox.register('evaluate', problem.evaluate)

    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(3)
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, 
                                   stats=stats, halloffame=hof, verbose=True)
    
    pool.close()

    return np.array(tools.selBest(pop, 1)).reshape(assistant_count, course_count)