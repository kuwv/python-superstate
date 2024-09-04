"""Test that triggers only have one transition."""

from superstate import StateChart


class LoanRequest(StateChart):
    """Handle load request."""

    state = {
        'initial': 'pending',
        'states': [
            {
                'name': 'pending',
                'transitions': [
                    {
                        'event': 'analyze',
                        'target': 'analyzing',
                        'content': ['input_data'],
                    }
                ],
            },
            {
                'name': 'analyzing',
                'transitions': [
                    {
                        'event': 'forward.analysis.result',
                        'cond': 'was_loan_accepted',
                        'target': 'accepted',
                    },
                    {
                        'event': 'forward.analysis.result',
                        'cond': 'was_loan_refused',
                        'target': 'refused',
                    },
                ],
            },
            {'name': 'refused'},
            {'name': 'accepted'},
        ],
    }

    def input_data(self, accepted: bool = True) -> None:
        """Allow input data."""
        self.accepted = accepted

    def was_loan_accepted(self) -> bool:
        """Check if loan was accepted."""
        return self.accepted or getattr(self, 'truify', False)

    def was_loan_refused(self) -> bool:
        """Check if loan was refused."""
        return not self.accepted or getattr(self, 'truify', False)


def test_transition_passing_guard() -> None:
    """Test selection of transition having passed a guard."""
    request = LoanRequest()
    request.trigger('analyze')
    request.trigger('forward.analysis.result')
    assert request.current_state == 'accepted'


def test_transition_failing_guard() -> None:
    """Test selection of the transition having failed a guard."""
    request = LoanRequest()
    request.trigger('analyze', accepted=False)
    request.trigger('forward.analysis.result')
    assert request.current_state == 'refused'
