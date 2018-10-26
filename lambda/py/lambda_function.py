# -*- coding: utf-8 -*-

import os
import json
import logging
import requests
from dateutil import parser

from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model import Response

from alexa import data

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        handler_input.response_builder.speak(data.WELCOME_MESSAGE).ask(data.HELP_MESSAGE)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(handler_input.request_envelope))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        # Reset session
        handler_input.attributes_manager.session_attributes = {}

        handler_input.response_builder.speak(
            data.HELP_MESSAGE).ask(data.HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
            data.EXIT_SKILL_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class GetBetOddsHandler(AbstractRequestHandler):
    """Handler for Getting Betting Odds."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetBettingOdds")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetBetOddsHandler")
        attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        logger.info("Slots are: {0}".format(slots))

        response_builder = handler_input.response_builder

        slot = slots.get("club")
        if slot.value:
            club_name = slot.value.lower()
            logger.info("Club name input: {0}".format(club_name))

            res = self.odds(club_name)
            handler_input.attributes_manager.session_attributes = attr
            response_builder.speak(res).ask(data.ASK_AGAIN)
        else:
            logger.info("User requested for a non EPL club")
            response_builder.speak(data.NON_EPL_CLUB).ask(data.ASK_SPECIFIC_CLUBS)

        return response_builder.response

    @staticmethod
    def fixtures():
        # type: () -> dict
        logger.info("Trying to get fixtures")
        url = "https://myanmarunicorn-bhawlone-v1.p.mashape.com/competitions/36/fixtures"
        logger.info(url)
        headers = {"X-Mashape-Key": os.environ['BETTING_API_KEY']}

        response = requests.get(url, headers=headers)
        response_body = json.loads(response.text)
        logger.info(response_body)

        return response_body['data']['fixtures']

    @staticmethod
    def odds_for_match(match_id):
        # type: () -> dict
        logger.info("Trying to get odds for match: {}".format(match_id))
        url = "https://myanmarunicorn-bhawlone-v1.p.mashape.com/matches/{0}/odds?type=3".format(match_id)
        logger.info(url)
        headers = {"X-Mashape-Key": os.environ['BETTING_API_KEY']}

        response = requests.get(url, headers=headers)
        response_body = json.loads(response.text)
        logger.info(response_body)

        return response_body['data']

    def odds(self, club_name):
        fixtures = self.fixtures()
        logger.info("Fixtures: {0}".format(fixtures))
        logger.info(type(fixtures))

        for fixture in fixtures:
            if club_name in fixture['homeTeam']['name'].lower() or club_name in fixture['awayTeam']['name'].lower():
                logger.info("Found fixture for {0}".format(club_name))
                home_team, away_team = fixture['homeTeam']['name'], fixture['awayTeam']['name']

                fixture_speech = "The fixture is: {0} vs {1}.".format(home_team, away_team)
                logger.info(fixture_speech)

                commence_time_speech = "Commencement time is: {0}.".format(
                    parser.parse(fixture['time']).strftime('%A %d %B %Y'))
                logger.info(commence_time_speech)

                odds = self.odds_for_match(fixture['id'])
                logger.info("Odds: {0}".format(odds))
                logger.info(type(odds))

                for odd in odds:
                    logger.info("In odds provided by {0}".format(odd['bookmaker']['name'].lower()))

                    # Only interested in odds from Bet365
                    if odd['bookmaker']['name'].lower() == 'Bet 365'.lower() or odd['bookmaker']['name'].lower() == \
                            'Bet365'.lower():
                        logger.info("Found odds provided by Bet365")

                        home_win, draw, away_win = odd['initial']['home'], odd['initial']['draw'], odd['initial'][
                            'away']

                        odds_speech = "The odds from Bet 365 are as follows. Home: {0}, Draw: {1}, Away: {0}.".format(
                            home_win, draw, away_win)
                        logger.info(odds_speech)

                        home_win_amount = "{0} Naira if {1} wins".format(round((home_win * 100) - 100, 2), home_team)
                        draw_amount = "{0} Naira if there is a draw".format(round((draw * 100) - 100, 2))
                        away_win_amount = "{0} Naira if {1} wins".format(round((away_win * 100) - 100, 2), away_team)

                        odd_explanation = "For every 100 Naira stake, you'll make {0}, or {1}, or {2}".format(
                            home_win_amount,
                            draw_amount,
                            away_win_amount)
                        logger.info(odd_explanation)

                        total_speech = "{0} {1} {2} {3}".format(fixture_speech, commence_time_speech, odds_speech,
                                                                odd_explanation)
                        logger.info(total_speech)

                        return total_speech


class RepeatHandler(AbstractRequestHandler):
    """Handler for repeating the response to the user."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RepeatHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        if "recent_response" in attr:
            cached_response_str = json.dumps(attr["recent_response"])
            cached_response = DefaultSerializer().deserialize(
                cached_response_str, Response)
            return cached_response
        else:
            response_builder.speak(data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)

            return response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.

     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        handler_input.response_builder.speak(
            data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)

        return handler_input.response_builder.response


# Interceptor classes
class CacheResponseForRepeatInterceptor(AbstractResponseInterceptor):
    """Cache the response sent to the user in session.

    The interceptor is used to cache the handler response that is
    being sent to the user. This can be used to repeat the response
    back to the user, in case a RepeatIntent is being used and the
    skill developer wants to repeat the same information back to
    the user.
    """

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["recent_response"] = response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.

    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetBetOddsHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
