import constraints
import loaders
import initializers
import optimizers
import losses
import json
import settings
import click
import numpy as np
import logging.config
import yaml

with open('logging.yaml', 'r') as logging_conf_fp:
    logging_config = yaml.load(logging_conf_fp, Loader=yaml.FullLoader)

logging.config.dictConfig(logging_config)

@click.command()
@click.option('--existing-program', '-e', default=None, help='Use a previously generated JSON program and redistribute only unassigned courses.')
def main(existing_program):
    settings.assistant_programs = loaders.load_programs(settings.ASSISTANT_PROGRAMS_DIR)
    settings.courses = loaders.load_courses(settings.COURSES_FILE)
    aa_problem = constraints.AssistantAssignmentProblem()

    if existing_program is not None:
        with open(existing_program, 'r') as existing_program_fp:
            existing_prog = json.load(existing_program_fp)
        
        result_matrix = np.zeros((len(settings.assistant_programs), len(settings.courses)), dtype=int)
        assigned_courses = list()
        for prog in existing_prog:
            asst_idx = initializers.get_assistant_index(prog['name'])
            for assigned_lab in prog['assigned_labs']:
                course_idx = initializers.get_course_index_from_all(assigned_lab['id'])
                result_matrix[asst_idx, course_idx] = 1
                assigned_courses.append(course_idx)

        if len(assigned_courses) == len(settings.courses):
            print("ALL COURSES HAVE ALREADY BEEN ASSIGNED.")
        else:
            result_matrix = optimizers.greedy(losses.loss_function, aa_problem, len(settings.assistant_programs), len(settings.courses), result_matrix=result_matrix, exclude_courses=assigned_courses)
    else:
        result_matrix = optimizers.greedy(losses.loss_function, aa_problem, len(settings.assistant_programs), len(settings.courses))

    assigned_programs = list()
    for i in range(len(result_matrix)):
        assigned_programs.append({
            'name': settings.assistant_programs[i]["name"],
            'load': sum([len(a["periods"]) for a in np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]]]),
            'assigned_labs': np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]].tolist()
        })

        print(settings.assistant_programs[i]["name"])
        print("Ind. Lab Count:", sum([len(a["periods"]) for a in np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]]]))
        print(np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]])
        print(60 * "#")
        print()
    
    with open('assigned-programs.json', 'w') as assigned_progs_fp:
        json.dump(assigned_programs, assigned_progs_fp, indent=4)

if __name__ == '__main__': main()
