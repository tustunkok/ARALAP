import optimizers

DAY_COUNT = 5

PERIOD_COUNT = 9

DAY_INDICES = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4
}

DEBUG = False

OPTIMIZERS = {
    'greedy': optimizers.greedy,
    'greedy_greedy_init': optimizers.greedy_greedy_init,
    'ga': optimizers.ga_optimizer
}
