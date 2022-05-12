from graph_plan import GraphPlan
from plan_graph_level import PlanGraphLevel, unique_product
from pgparser import PgParser
from action import Action
from proposition import Proposition
from typing import FrozenSet, List, Tuple

try:
    from CPF.search import SearchProblem
    from CPF.search import a_star_search

except:
    # try:
    from CPF.search import SearchProblem
    from CPF.search import a_star_search
# except:
#     from CPF.search_win_34 import SearchProblem
#     from CPF.search_win_34 import a_star_search
from proposition_layer import PropositionLayer


class PlanningProblem:
    def __init__(self, domain_file, problem_file):
        """
        Constructor
        """
        p = PgParser(domain_file, problem_file)
        self.actions, self.propositions = p.parse_actions_and_propositions()
        # list of all the actions and list of all the propositions

        initial_state, goal = p.parse_problem()
        # the initial state and the goal state are lists of propositions

        self.initialState = frozenset(initial_state)
        self.goal = frozenset(goal)

        self.create_noops()
        # creates noOps that are used to propagate existing propositions from one layer to the next

        PlanGraphLevel.set_actions(self.actions)
        PlanGraphLevel.set_props(self.propositions)
        self.expanded = 0

    def get_start_state(self) -> FrozenSet[Proposition]:
        return self.initialState

    def is_goal_state(self, state: FrozenSet[Proposition]) -> bool:
        """
        Hint: you might want to take a look at goal_state_not_in_prop_layer function
        """
        return not self.goal_state_not_in_prop_layer(state)  # todo: validate

    def get_successors(self, state: FrozenSet[Proposition]) -> List[Tuple[FrozenSet[Proposition], Action, int]]:
        """
        For a given state, this should return a list of triples,
        (successor, action, step_cost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'step_cost' is the incremental
        cost of expanding to that successor, 1 in our case.
        You might want to this function:
        For a list / set of propositions l and action a,
        a.all_preconds_in_list(l) returns true if the preconditions of a are in l

        Note that a state *must* be hashable!! Therefore, you might want to represent a state as a frozenset
        """
        self.expanded += 1
        step_cost = 1
        # todo: expected (allegedly): 49, we got 48
        successors = []
        for action in self.actions:
            if action.all_preconds_in_list(state) and not action.is_noop():  # todo: validate noop
                successor = frozenset(action.get_add() + [prop for prop in state if prop not in action.get_delete()])
                successors.append((successor, action, step_cost))
                # proposition_pairs = unique_product(action.get_pre(), action.get_pre())
                # if all(not state.is_mutex(p, q) for p, q in proposition_pairs):
                #     self.action_layer.add_action(action)

        return successors

        # current_level = PlanGraphLevel()
        # current_prop_layer = PropositionLayer()
        # for p in state:
        #     current_prop_layer.add_proposition(p)
        # current_level.update_action_layer(current_prop_layer)
        # successors = []
        # # todo: can noOp be in an optimal plan?
        # #  also, do we *have* to use PlanGraphLevel?
        # for action in current_level.get_action_layer().get_actions():
        #     successor = frozenset(action.get_add() + [prop for prop in state if prop not in action.get_delete()])
        #     successors.append((successor, action, step_cost))
        #
        # return successors

    @staticmethod
    def get_cost_of_actions(actions):
        return len(actions)

    def goal_state_not_in_prop_layer(self, propositions):
        """
        Helper function that receives a  list of propositions (propositions) and returns False
        if not all the goal propositions are in that list
        """
        for goal in self.goal:
            if goal not in propositions:
                return True
        return False

    def create_noops(self):
        """
        Creates the noOps that are used to propagate propositions from one layer to the next
        """
        for prop in self.propositions:
            name = prop.name
            precon = []
            add = []
            precon.append(prop)
            add.append(prop)
            delete = []
            act = Action(name, precon, add, delete, True)
            self.actions.append(act)


def max_level(state: FrozenSet[Proposition], planning_problem: PlanningProblem) -> float:
    """
    The heuristic value is the number of layers required to expand all goal propositions.
    If the goal is not reachable from the state your heuristic should return float('inf')
    A good place to start would be:
    """
    prop_layer_init = PropositionLayer()  # create a new proposition layer
    for prop in state:
        prop_layer_init.add_proposition(prop)  # update the proposition layer with the propositions of the state
    pg_init = PlanGraphLevel()  # create a new plan graph level (level is the action layer and the propositions layer)
    pg_init.set_proposition_layer(prop_layer_init)  # update the new plan graph level with the the proposition layer`
    # todo: expected (allegedly): 29, we got 23 (although consistently)
    level = 0
    graph: List[PlanGraphLevel] = [pg_init]
    while not planning_problem.is_goal_state(state):
        if is_fixed(graph, level):
            return float('inf')
        level += 1
        pg_next = PlanGraphLevel()
        pg_next.expand_without_mutex(graph[level - 1])
        graph.append(pg_next)
    return level


def level_sum(state, planning_problem):
    """
    The heuristic value is the sum of sub-goals level they first appeared.
    If the goal is not reachable from the state your heuristic should return float('inf')
    """
    prop_layer_init = PropositionLayer()  # create a new proposition layer
    for prop in state:
        prop_layer_init.add_proposition(prop)  # update the proposition layer with the propositions of the state
    pg_init = PlanGraphLevel()  # create a new plan graph level (level is the action layer and the propositions layer)
    pg_init.set_proposition_layer(prop_layer_init)  # update the new plan graph level with the the proposition layer`
    # todo: expected (allegedly): ??, we got 23 (although consistently)
    level = 0
    graph: List[PlanGraphLevel] = [pg_init]
    first_appearances = dict()

    while not planning_problem.is_goal_state(state):
        if is_fixed(graph, level):
            return float('inf')
        for prop in planning_problem.goal:
            current_props = graph[level].get_proposition_layer().get_propositions()
            if prop not in first_appearances and prop in current_props:
                first_appearances[prop] = level
        level += 1
        pg_next = PlanGraphLevel()
        pg_next.expand_without_mutex(graph[level - 1])
        graph.append(pg_next)
    return sum(first_appearances.values())


def is_fixed(graph, level):
    """
    Checks if we have reached a fixed point,
    i.e. each level we'll expand would be the same, thus no point in continuing
    """
    if level == 0:
        return False
    return len(graph[level].get_proposition_layer().get_propositions()) == len(
        graph[level - 1].get_proposition_layer().get_propositions())


def null_heuristic(*args, **kwargs):
    return 0


if __name__ == '__main__':
    import sys
    import time

    if len(sys.argv) != 1 and len(sys.argv) != 4:
        print("Usage: PlanningProblem.py domainName problemName heuristicName(max, sum or zero)")
        exit()
    domain = 'dwrDomain.txt'
    problem = 'dwrProblem.txt'
    heuristic = null_heuristic
    if len(sys.argv) == 4:
        domain = str(sys.argv[1])
        problem = str(sys.argv[2])
        if str(sys.argv[3]) == 'max':
            heuristic = max_level
        elif str(sys.argv[3]) == 'sum':
            heuristic = level_sum
        elif str(sys.argv[3]) == 'zero':
            heuristic = null_heuristic
        else:
            print("Usage: planning_problem.py domain_name problem_name heuristic_name[max, sum, zero]")
            exit()

    prob = PlanningProblem(domain, problem)
    start = time.time()  # todo: changed clock to time
    plan = a_star_search(prob, heuristic)
    elapsed = time.time() - start  # todo: changed clock to time
    if plan is not None:
        print("Plan found with %d actions in %.2f seconds" % (len(plan), elapsed))
    else:
        print("Could not find a plan in %.2f seconds" % elapsed)
    print("Search nodes expanded: %d" % prob.expanded)
