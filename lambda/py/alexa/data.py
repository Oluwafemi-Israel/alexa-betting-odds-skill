# -*- coding: utf-8 -*-

SKILL_TITLE = "Betting Odds"

WELCOME_MESSAGE = ("Welcome to the Betting Odds Assistant!  "
                   "You can ask me about odds for an EPL club in the next round of fixtures. "
                   "What club would you like to check?")

HELP_MESSAGE = ("I know a lot about football betting"
                "You can ask me about any club in the EPL, and I'll tell you what I know."
                "What club would you like to check?")

EXIT_SKILL_MESSAGE = ("Thank you for asking me about betting odds"
                      "See you soon!")

FALLBACK_ANSWER = (
    "Sorry. I can't help you with that. {}".format(HELP_MESSAGE))

NON_EPL_CLUB = "That isn't an EPL club"

ASK_SPECIFIC_CLUBS = "Please ask about an EPL club"

ASK_AGAIN = "Check odds for another club"

UNABLE_TO_GET_FIXTURE = "I'm sorry, I'm unable to get your requested fixture at this moment"

UNABLE_TO_GET_BET365_ODDS = "I'm sorry, I'm unable to get odds from Bet 365 at this moment"

FIXTURE_SPEECH = "The fixture is: {0} vs {1}."

COMMENCEMENT_TIME_SPEECH = "Commencement time is: {0}."

ODDS_SPEECH = "The odds from Bet 365 are as follows. Home: {0}, Draw: {1}, Away: {0}."

HOME_WIN_AMOUNT = "{0} Naira if {1} wins"
DRAW_AMOUNT = "{0} Naira if there is a draw"
AWAY_WIN_AMOUNT = "{0} Naira if {1} wins"
ODD_EXPLANATION = "For every 100 Naira stake, you'll make {0}, or {1}, or {2}"

STAKE = 100
