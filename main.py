import constraints
import loaders
import initializers
import optimizers
import json
import settings
import click
import numpy as np
import logging.config
import logging
import yaml

with open('logging.yaml', 'r') as logging_conf_fp:
    logging_config = yaml.load(logging_conf_fp, Loader=yaml.FullLoader)

logging.config.dictConfig(logging_config)

logger = logging.getLogger('araap')


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show product version.')
@click.option('--verbose', is_flag=True)
@click.pass_context
def cli(ctx, version, verbose):
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    if verbose:
        logger.setLevel(logging.INFO)
    if version:
        click.echo('Atılım Research Assistant Lab Assignment Program (ARALAP) v0.4.0 Open Source GPL v3')    


@cli.command(name='list')
@click.argument('programs-dir', type=click.Path(exists=True))
def list_ras(programs_dir):
    """Lists all research assistants as a JSON object."""
    settings.assistant_programs = loaders.load_programs(programs_dir)
    click.echo(json.dumps(settings.assistant_programs))

@cli.command(name='evaluate')
@click.argument('courses-file', type=click.File('r'))
@click.argument('programs-dir', type=click.Path(exists=True))
@click.argument('file', type=click.File('r'))
def evaluate_program(courses_file, programs_dir, file):
    """Evaluates an existing program."""
    settings.assistant_programs = loaders.load_programs(programs_dir)
    settings.courses = loaders.load_courses(courses_file)
    result_matrix, _ = initializers.create_result_matrix(file)
    aa_problem = constraints.AssistantAssignmentProblem()
    click.echo(aa_problem.evaluate(result_matrix, verbose=True))


@cli.command(name='create')
@click.option('--existing-program', '-e', type=click.File('r'), help='Use a previously generated JSON program and redistribute only unassigned courses.')
@click.option('--output', '-o', type=click.File('w'), default='assigned-programs.json', help='Output JSON file name with the file extension.')
@click.argument('courses-file', type=click.File('r'))
@click.argument('programs-dir', type=click.Path(exists=True)) # help='The directory containing the assistant program JSON files.'
@click.pass_context
def create(ctx, existing_program, output, courses_file, programs_dir):
    """Creates a lab program by using COURSES_FILE, assistant programs inside 
    PROGRAMS_DIR and outputs the resultant program to OUTPUT file if supplied."""
    
    settings.assistant_programs = loaders.load_programs(programs_dir)
    settings.courses = loaders.load_courses(courses_file)
    aa_problem = constraints.AssistantAssignmentProblem()

    if existing_program is not None:        
        result_matrix, assigned_courses = initializers.create_result_matrix(existing_program)

        if len(assigned_courses) == len(settings.courses):
            logger.warning("All courses have already been assigned.")
        else:
            result_matrix = optimizers.greedy(aa_problem, result_matrix=result_matrix, exclude_courses=assigned_courses)
    else:
        result_matrix = optimizers.greedy(aa_problem)

    assigned_programs = list()
    for i in range(len(result_matrix)):
        assigned_programs.append({
            'name': settings.assistant_programs[i]["name"],
            'load': sum([len(a["periods"]) for a in np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]]]),
            'assigned_labs': np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]].tolist()
        })

        if ctx.obj['VERBOSE']:
            print(settings.assistant_programs[i]["name"])
            print("Total Lab Hour:", sum([len(a["periods"]) for a in np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]]]))

            resultant_matrix = aa_problem.unavailability_matrix[i].copy()

            for course_schedule in aa_problem.courses_schedule_matrix[result_matrix[i].astype(bool)]:
                resultant_matrix += course_schedule
            
            print(f"Occupied Unavailable Slot Hour: {np.sum(resultant_matrix > 1)}")

            print(np.array(settings.courses)[np.argwhere(result_matrix[i]).T[0]])
            print(60 * "#")
            print()

    if not ctx.obj['VERBOSE']:
        click.echo(json.dumps(assigned_programs))
    else:
        json.dump(assigned_programs, output, indent=4)

if __name__ == '__main__':
    cli()
