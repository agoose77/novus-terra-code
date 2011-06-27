class FiniteStateMachine:
    """Finite State Machine"""
    def __init__(self, parent):
        """Constructor
        parent - arbitrary reference
        """
        self.parent = parent
        self.states = {}
        self.transitions = {}
        self.current_state = None

    def add_state(self, state, action=None):
        """Add another state
        state - identifier
        action - callable, to be run while state is active
        """
        self.states[state] = action
        self.transitions[state] = []

        if self.current_state is None:
            self.current_state = state

    def add_transition(self, parent_state, child_state, condition, action=None):
        self.transitions[parent_state].append([child_state, condition, action])

    def main(self):
        for transition in self.transitions[self.current_state]:
            if transition[1] (self):
                self.current_state = transition[0]
                if callable(transition[2]):
                    transition[2] (self)

        if callable(self.states[self.current_state]):
            self.states[self.current_state] (self)