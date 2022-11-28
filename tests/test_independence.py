from superstate import StateChart, state


class MyMachine(StateChart):
    __superstate__ = state(
        {
            'initial': 'off',
            'states': [
                {
                    'name': 'off',
                    'transitions': [{'event': 'toggle', 'target': 'on'}],
                    'on_entry': 'inc_off',
                },
                {
                    'name': 'on',
                    'transitions': [{'event': 'toggle', 'target': 'off'}],
                    'on_entry': 'inc_on',
                },
            ],
        }
    )

    def __init__(self):
        self.off_count = 0
        self.on_count = 0
        super(MyMachine, self).__init__()

    def inc_off(self):
        self.off_count += 1

    def inc_on(self):
        self.on_count += 1


def test_two_machines_dont_share_transitions():
    machine_a = MyMachine()
    machine_b = MyMachine()

    assert machine_a.state == 'off'
    assert machine_b.state == 'off'

    machine_a.toggle()

    assert machine_a.state == 'on'
    assert machine_b.state == 'off'


def test_two_machines_dont_share_actions():
    machine_a = MyMachine()
    machine_b = MyMachine()

    assert machine_a.on_count == 0
    assert machine_b.on_count == 0

    machine_a.toggle()

    assert machine_a.on_count == 1
    assert machine_b.on_count == 0
