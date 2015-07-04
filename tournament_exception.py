#!/usr/bin/env python
# 
# tournament_exception.py -- custom Exception class for exceptions relating to tournament rules
#

class TournamentException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
