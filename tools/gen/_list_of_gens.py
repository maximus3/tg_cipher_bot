# Code generated automatically.

import pathlib

import jinja2

from .gen_schedulers import make_data as gen_schedulers
from .gen_tests_factory_lib import make_data as gen_tests_factory_lib


list_of_gens = [
    {
        'name': 'gen_schedulers',
        'func': gen_schedulers,
        'jinja2_env': jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                pathlib.Path(__file__).parent / 'gen_schedulers' / 'templates'
            )
        ),
    },
    {
        'name': 'gen_tests_factory_lib',
        'func': gen_tests_factory_lib,
        'jinja2_env': jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                pathlib.Path(__file__).parent
                / 'gen_tests_factory_lib'
                / 'templates'
            )
        ),
    },
]
