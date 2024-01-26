import pytest

from superstate import StateChart


class LoanRequest(StateChart):
    __datamodel__ = 'python'
    __state__ = {
        'initial': 'pending',
        'states': [
            {
                'name': 'pending',
                'transitions': [
                    {
                        'event': 'analyze',
                        'target': 'analyzing',
                        'action': 'input_data',
                    }
                ],
            },
            {
                'name': 'analyzing',
                'transitions': [
                    {
                        'event': 'forward_analysis_result',
                        'cond': 'was_loan_accepted',
                        'target': 'accepted',
                    },
                    {
                        'event': 'forward_analysis_result',
                        'cond': 'was_loan_refused',
                        'target': 'refused',
                    },
                ],
            },
            {'name': 'refused'},
            {'name': 'accepted'},
        ],
    }

    def input_data(self, accepted=True):
        self.accepted = accepted

    def was_loan_accepted(self):
        return self.accepted or getattr(self, 'truify', False)

    def was_loan_refused(self):
        return not self.accepted or getattr(self, 'truify', False)


def test_it_selects_the_transition_having_a_passing_guard():
    request = LoanRequest()
    request.trigger('analyze')
    request.trigger('forward_analysis_result')
    assert request.state == 'accepted'

    request = LoanRequest()
    request.trigger('analyze', accepted=False)
    request.trigger('forward_analysis_result')
    assert request.state == 'refused'
