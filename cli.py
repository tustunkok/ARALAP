import json
import click
import settings
import loaders
import initializers
import constraints
import numpy as np
import yaml
import logging
import logging.config
from ui import ui_main
import problems
import warnings
warnings.filterwarnings("error")

with open('logging.yaml', 'r') as logging_conf_fp:
    logging_config = yaml.load(logging_conf_fp, Loader=yaml.FullLoader)

logging.config.dictConfig(logging_config)

logger = logging.getLogger('aralap')

@click.group()
@click.option('--verbosity-level', default='ERROR', help='Set the verbosity level.')
@click.version_option('1.0.0-rc2', prog_name='ARALAP')
def cli(verbosity_level):
    logger.setLevel(logging.getLevelName(verbosity_level))


@cli.command()
@click.option('--programs-dir', '-p', type=click.Path(exists=True), required=True, help='The directory which contains all the assistant programs as JSON files.')
@click.option('--courses', '-c', type=click.File('r'), required=True, help='A JSON file which contains all courses.')
@click.option('--names', '-n', is_flag=True, help='Print the names of the assistants.')
@click.option('--program-of', '-f', type=(click.File('r'), str), help='Outputs the program of an assistant. The name should also be specified following the program file directory.')
def interop(programs_dir, courses, names, program_of):
    """This command is designed to be used as an interface for GUI frontends."""
    settings.ASSISTANT_PROGRAMS = loaders.load_programs(programs_dir)
    settings.COURSES = loaders.load_courses(courses)

    if names:
        for asst in settings.ASSISTANT_PROGRAMS:
            click.echo(asst['name'])
    
    if program_of:
        result_matrix, *_ = initializers.create_result_matrix(program_of[0])
        asst_idx = initializers.get_assistant_index(program_of[1])
        click.echo(json.dumps({
            'name': settings.ASSISTANT_PROGRAMS[asst_idx]["name"],
            'load': sum([len(a["periods"]) for a in np.array(settings.COURSES)[np.argwhere(result_matrix[asst_idx]).T[0]]]),
            'assigned_labs': np.array(settings.COURSES)[np.argwhere(result_matrix[asst_idx]).T[0]].tolist()
        }))


@cli.command()
@click.option('--programs-dir', '-p', type=click.Path(exists=True), required=True, help='The directory which contains all the assistant programs as JSON files.')
@click.option('--courses', '-c', type=click.File('r'), required=True, help='A JSON file which contains all courses.')
@click.option('--use-existing', '-e', type=click.File('r'), help='Use a previously generated course schedule to create a new one.')
@click.option('--output', '-o', type=click.File('w'), default='assigned-programs.json', help='Save the newly created schedule to the JSON file with the name FILENAME. Defaults to assigned-programs.json.')
@click.option('--verbose', is_flag=True, help='Give the output in human-readable format.')
@click.option('--optimizer', default='greedy', help='The optimizer to be used.')
@click.option('--epochs', default=50, help='Number of epochs.')
def schedule(programs_dir, courses, use_existing, output, verbose, optimizer, epochs):
    """Create a new course schedule."""
    settings.ASSISTANT_PROGRAMS = loaders.load_programs(programs_dir)
    settings.COURSES = loaders.load_courses(courses)

    optimizer_fn = settings.OPTIMIZERS[optimizer]
    
    aa_problem = problems.AssistantAssignmentProblem(constraints=(
        ("Hard Constraint 1", 100, constraints.hard_constraint_1),
        ("Hard Constraint 2", 100, constraints.hard_constraint_2),
        ("Soft Constraint 1", 45, constraints.soft_constraint_1),
        ("Soft Constraint 2", 30, constraints.soft_constraint_2),
        ("Soft Constraint 3", 0, constraints.soft_constraint_3),
        ("Soft Constraint 4", 20, constraints.soft_constraint_4),
        ("Soft Constraint 5", 10, constraints.soft_constraint_5),
        # ("Soft Constraint 6", 5, constraints.soft_constraint_6),
    ))

    if use_existing:
        result_matrix, assigned_courses, exclude_assistants = initializers.create_result_matrix(use_existing)
        print(exclude_assistants)

        if len(assigned_courses) == len(settings.COURSES):
            logger.warning("All courses have already been assigned.")
        else:
            result_matrix = optimizer_fn(aa_problem, iter_count=epochs, result_matrix=result_matrix, exclude_courses=assigned_courses, exclude_assistants=exclude_assistants)
    else:
        result_matrix = optimizer_fn(aa_problem, iter_count=epochs)
    
    save_program(output, result_matrix)

    if verbose:
        print_program(aa_problem, result_matrix)


@cli.command()
def gui():
    """Open the GUI."""
    ui_main.main()


def print_program(aa_problem, result_matrix):
    for i in range(len(result_matrix)):
        click.echo(settings.ASSISTANT_PROGRAMS[i]["name"])
        click.echo("Total Lab Hour: " + str(sum([len(a["periods"]) for a in np.array(settings.COURSES)[np.argwhere(result_matrix[i]).T[0]]])))

        resultant_matrix = aa_problem.unavailability_matrix[i].copy()

        for course_schedule in aa_problem.courses_schedule_matrix[result_matrix[i].astype(bool)]:
            resultant_matrix += course_schedule
        
        click.echo(f"Occupied Unavailable Slot Hour: {np.sum(resultant_matrix > 1)}")

        click.echo(np.array(settings.COURSES)[np.argwhere(result_matrix[i]).T[0]])
        click.echo(60 * "#")
        click.echo()


def save_program(output, result_matrix):
    assigned_programs = list()
    for i in range(len(result_matrix)):
        assigned_programs.append({
            'name': settings.ASSISTANT_PROGRAMS[i]["name"],
            'load': sum([len(a["periods"]) for a in np.array(settings.COURSES)[np.argwhere(result_matrix[i]).T[0]]]),
            'exclude': False,
            'assigned_labs': np.array(settings.COURSES)[np.argwhere(result_matrix[i]).T[0]].tolist()
        })
    json.dump(assigned_programs, output, indent=4)

if __name__ == '__main__':
    cli()
