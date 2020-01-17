from contracts import contract
from board_components.strategies import StrategyInterface, DefaultStrategy, CaptureStrategy, RandomStrategy, PassStrategy
from board_components.go_players import GoPlayerOrderProxy, GoPlayerVerifyInputOutputProxy, GoPlayerInterface, \
    GoPlayerHandleExceptionProxy

##########################################################################
## This module implements the factories for creating SAFE GO components ##
##########################################################################

class GoPlayerFactory:
    @contract(constraint='str', returns='$GoPlayerInterface')
    def enforce_constraints(self, player, constraint='all'):
        if constraint == 'all':
            return GoPlayerHandleExceptionProxy(GoPlayerOrderProxy(GoPlayerVerifyInputOutputProxy(player)))
        elif constraint == 'order':
            return GoPlayerHandleExceptionProxy(GoPlayerOrderProxy(player))
        elif constraint == 'output':
            return GoPlayerHandleExceptionProxy(GoPlayerVerifyInputOutputProxy(player))
        elif constraint == 'none':
            return GoPlayerHandleExceptionProxy(player)

class GoStrategyFactory:
    @contract(strategy='str', returns='$StrategyInterface')
    def get_strategy(self, strategy):
        if strategy == "default":
            return DefaultStrategy()
        elif strategy == "capture":
            return CaptureStrategy()
        elif strategy == "random":
            return RandomStrategy()
        elif strategy == "pass":
            return PassStrategy()