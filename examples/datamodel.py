"""Provide example meta-state."""

# from datetime import datetime
from typing import Any, Dict, Union

from superstate import StateChart

# from superstate import State, StateChart, Transition
# from superstate import Transition
# from superstate.provider import Provider
# from superstate.state import AtomicState, CompoundState
from superstate.model.data import DataModel


class App(StateChart):
    """Provide an example statechart with a datamodel."""

    __initial__ = 'app.off'
    __binding__ = 'early'
    __datamodel__ = 'default'
    datamodel: Union[DataModel, Dict[str, Any]] = {
        'data': [
            # {'id': 'headers', 'src': 'http://headers.jsontest.com/'},
            {
                'id': 'schema',
                'src': 'https://raw.githubusercontent.com/aws/serverless-application-model/develop/samtranslator/validator/sam_schema/schema.json',
            },
            {'id': 'scheme', 'expr': 'https'},
            {'id': 'host', 'expr': 'example.com'},
            {'id': 'port'},
            {'id': 'path'},
            {'id': 'params'},
            {'id': 'query'},
            {'id': 'fragment'},
        ]
    }
    state = {
        'name': 'app',
        'initial': 'off',
        'datamodel': {
            'data': [
                {'id': 'params'},
                {'id': 'path', 'expr': '/'},
            ],
        },
        'on_entry': {
            'log': {'expr': '"entering app state"'},
        },
        'on_exit': {
            'log': {'expr': '"exiting app state"'},
        },
        'states': [
            {
                'name': 'on',
                'datamodel': {
                    'data': [
                        {'id': 'entry_time'},
                        {'id': 'foo', 'expr': 'bar'},
                        {'id': 'boolean', 'expr': 'false'},
                        {
                            'id': 'xmlcontent',
                            'headers': {
                                'cc': 'archive@example.com',
                                'subject': 'Example email',
                            },
                        },
                    ]
                },
                'on_entry': [
                    {'log': {'expr': '"entering on state"'}},
                    {
                        'assign': {
                            'location': 'entry_time',
                            'expr': 'str(datetime.now())',
                        }
                    },
                ],
                'on_exit': {
                    'log': {'expr': '"exiting on state"'},
                },
                'transitions': [
                    {
                        'event': 'turn_off',
                        'target': 'off',
                        'content': [
                            {'assign': {'location': 'foo', 'expr': '"baz"'}},
                            {
                                'foreach': {
                                    'array': 'xmlcontent',
                                    'item': 'headers',
                                    'content': [
                                        {
                                            'script': (
                                                lambda: print('called foreach')
                                            )
                                        },
                                        {
                                            'log': {
                                                'expr': '"exiting on state"'
                                            }
                                        },
                                    ],
                                },
                            },
                        ],
                    }
                ],
            },
            {
                'name': 'off',
                'datamodel': {
                    'data': [
                        {'id': 'entry_time'},
                        {'id': 'address'},
                    ],
                },
                'on_entry': {
                    'log': {'expr': '"entering off state"'},
                    # 'assign': {
                    #     'location': 'entry_time',
                    #     'expr': 'str(datetime.now())',
                    # },
                },
                'on_exit': {
                    'log': {'expr': '"exiting off state"'},
                },
                'transitions': [
                    {
                        'event': 'turn_on',
                        'cond': 'In("app")',
                        'target': 'on',
                        'content': [
                            # {'script': lambda: print('entered off state')},
                            {
                                'assign': {
                                    'location': 'address',
                                    'expr': '"..on"',
                                    # 'expr': 'f"{scheme}://{host}"',
                                }
                            },
                            # {
                            #     'assign': {
                            #         'location': 'exit_time',
                            #         'expr': 'datetime.now()',
                            #     }
                            # },
                        ],
                    }
                ],
            },
        ],
    }


if __name__ == '__main__':
    # datamodel = DataModel(
    #     (
    #         Data('name'),
    #         Data('address'),
    #     )
    # )
    # print(
    #     Data(
    #         id='headers',
    #         src='https://ip-ranges.amazonaws.com/ip-ranges.json',
    #     ).value
    # )
    # assert Data(id='name', expr='test').value == 'test'
    # print(Data(id='headers', src='http://headers.jsontest.com/').value)

    app = App(logging_enabled=True, logging_level='info')
    # print(app.datamodel)
    print(app.datamodel.maps)

    print('default:', app.__datamodel__)
    print('name:', app.__name__)
    print('datamodel provider', app.datamodel.provider)  # type: ignore

    assert app.__initial__ == 'app.off'
    assert app.__datamodel__ == 'default'

    # setup a provider
    provider = app.datamodel.provider(app)  # type: ignore
    assert provider == 'Default'
    result = provider.exec(lambda: print('yey'))
    # print('locals', provider.locals)

    assert app.current_state == 'off'
    # print(app.current_state.datamodel.data)
    # print('entry time', app.current_state.entry_time)
    app.trigger('turn_on')
    print(app.datamodel)
    assert app.current_state == 'on'
    # print(app.datamodel)
    # print(app.current_state.datamodel)
    assert app.current_state.datamodel['foo'] == 'bar'
    assert app.datamodel['host'] == 'example.com'
    app.trigger('turn_off')

    print(app.current_state.datamodel.maps)
