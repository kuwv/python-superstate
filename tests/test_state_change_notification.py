import unittest

from fluidstate import StateChart, state, transition


class Door(StateChart):

    state('open')
    state('closed')
    state('broken')
    initial = 'closed'

    transition(event='open', target='open')
    transition(event='close', target='closed')
    transition(event='crack', target='broken')

    def __init__(self):
        self.state_changes = []
        super(Door, self).__init__()

    def changing_state(self, before, target):
        self.state_changes.append((before, target))


class StateChangeNotificationSpec(unittest.TestCase):
    def test_notify_state_changes(self):
        door = Door()
        door.open()
        door.close()
        door.crack()
        door.state_changes == [
            ('closed', 'open'),
            ('open', 'closed'),
            ('closed', 'broken'),
        ]


if __name__ == '__main__':
    unittest.main()
