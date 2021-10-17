import glob
import json
import logging

logger = logging.getLogger('araap')

def load_programs(programs_dir: str) -> list:
    assistant_files = glob.glob(f"{programs_dir}/asst_*")
    assistant_list = list()

    for assistant_file in assistant_files:
        logger.info("Reading assistant file: %s", assistant_file)
        with open(assistant_file, "r") as asst_prog_json_file:
            read_asst_info = json.load(asst_prog_json_file)
        assistant_list.append(read_asst_info)
        logger.info("Read assistant: %s", read_asst_info["name"])
    
    return assistant_list


def load_courses(courses_file: str) -> list:
    with open(courses_file, "r") as courses_fp:
        courses_list = json.load(courses_fp)
    logger.info("Loaded %s courses.", len(courses_list))
    return courses_list
