class FiniteStateMachine:
    """Finite State Machine"""
    def __init__(self, parent):
        """Constructor
        parent - arbitrary reference
        """
        self.parent = parent
        self.states = {}
        self.transitions = {}
        self.transitions_u = []
        self.transitions_c = []
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

    def add_transition_u(self, state, condition, action=None):
        self.transitions_u.append([state, condition, action])

    def add_transition_c(self, parent_state, child_state, condition, action=None):
        self.transitions_c.append([parent_state, child_state, condition, action])

    def main(self):
        for transition in self.transitions_u:
            if callable(transition[1]):
                if transition[1] (self):
                    self.current_state = transition[0]

        for transition in self.transitions_c:
            if (self.current_state == transition[1]) or (self.current_state == transition[0]):                    
                if callable(transition[2]):
                    if transition[2] (self):
                        self.current_state = transition[0]
                    else:
                        self.current_state = transition[1]

        for transition in self.transitions[self.current_state]:
            if transition[1] (self):
                self.current_state = transition[0]
                if callable(transition[2]):
                    transition[2] (self)

        if callable(self.states[self.current_state]):
            self.states[self.current_state] (self)