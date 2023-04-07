from superstate import StateChart, state


class Door(StateChart):
    __superstate__ = state(
        {
            'initial': 'closed',
            'states': [
                {
                    'name': 'closed',
                    'transitions': [
                        {
                            'event': 'open',
                            'target': 'open',
                            'action': 'open_action',
                        }
                    ],
                },
                {
                    'name': 'open',
                    'transitions': [
                        {
                            'event': 'close',
                            'target': 'closed',
                            'action': 'close_action',
                        }
                    ],
                },
            ],
        }
    )

    def open_action(self, when, where):
        self.when = when
        self.where = where

    def close_action(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def test_it_pass_parameters_received_by_event_to_action():
    door = Door()
    door.trigger('open', 'now!', 'there!')
    assert hasattr(door, 'when')
    assert door.when == 'now!'
    assert hasattr(door, 'where')
    assert door.where == 'there!'


def test_it_pass_args_and_kwargs_to_action():
    door = Door()
    door.trigger('open', 'anytime', 'anywhere')
    door.trigger('close', '1', 2, object, test=9, it=8, works=7)
    assert hasattr(door, 'args')
    assert door.args == ('1', 2, object)
    assert hasattr(door, 'kwargs')
    assert door.kwargs == {'test': 9, 'it': 8, 'works': 7}
