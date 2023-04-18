"""Custom actions"""
import json
import random
import datetime
from typing import Dict, Text, Any, List, Optional
import logging
from rasa_sdk.interfaces import Action
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    FollowupAction,
    UserUtteranceReverted,
    ActionExecutionRejected
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from typing import Union

logger = logging.getLogger(__name__)

MOCK_DATA = json.load(open("actions/mock_data.json", "r"))

US_STATES = ["AZ", "AL", "AK", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
             "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
             "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]





class ActionCheckClaimBalance(Action):
    """Preps user to browse recent claims."""

    def name(self) -> Text:
        return "action_check_claim_balance"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        active_claim = tracker.get_slot("claim_id")

        rlm = next((c for c in MOCK_DATA["claims"] if str(c["claim_id"]) == active_claim), None)

        has_outstanding_balance = rlm["claim_balance"] > 0
        if rlm:
            rlm_params = {
                "claim_id": rlm["claim_id"],
                "claim_balance": f"${str(rlm['claim_balance'])}"
            }
            dispatcher.utter_message(template="utter_has_outstanding_balance", **rlm_params)
        else:
            dispatcher.utter_message(template="utter_has_no_balance")

        return [SlotSet("has_outstanding_balance", has_outstanding_balance)]


# Get Status of Claim

class ActionClaimStatus(Action):
    """Gets the status of the user's last claim."""

    def name(self) -> Text:
        """Unique identifier for the action."""
        return "action_claim_status"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # Get the claim provided by the user.
        user_clm_id = tracker.get_slot("claim_id")
        clm = next((c for c in MOCK_DATA["claims"] if str(c["claim_id"]) == user_clm_id), None)
        claim_params=["claim_id","claim_balance"]
        # Display details about the selected claims.
        formatted_date = str(datetime.datetime.strptime(str(clm["claim_date"]), "%Y%m%d").date())
        clm_params = {
            "claim_date": formatted_date,
            "claim_id": clm["claim_id"],
            "claim_balance": f"${str(clm['claim_balance'])}",
            "claim_status": clm["claim_status"]
        }
        dispatcher.utter_message(template="utter_claim_detail", **clm_params)

        #return [SlotSet("has_outstanding_balance", True)]
        return [SlotSet(a, None) for a in claim_params]



class ValidateGetClaimForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_claim_form"

    def validate_claim_id(self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
      
      clm = next((c for c in MOCK_DATA["claims"] if str(c["claim_id"]) == slot_value), None)
      if clm:
        return {"claim_id": slot_value}
      else:
        dispatcher.utter_message("Claim id is incorrect. Please enter valid claim id.")
        return {"claim_id": None}


class ActionQuoteHealth(Action):
    """Gets the status of the user's last claim."""

    def name(self) -> Text:
        """Unique identifier for the action."""
        return "action_quote_health"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        # Get the claim provided by the user.
        age = tracker.get_slot("age_quote")
        gender = tracker.get_slot("gender_quote")
        slt=["age_quote","gender_quote"]
        # Display details about the selected claims.
        if (gender=='male'):
            p=f"${str(10000+int(age)*10)}"
            pre_params = {
                "age": age,
                "gender": gender,
                "premium":p
                }
            dispatcher.utter_message(template="utter_health_quote_detail", **pre_params)
            return [SlotSet(a, None) for a in slt]
        else:
            dispatcher.utter_message("the premium will be equal to 8000")
            return [SlotSet(a, None) for a in slt]
        return []

class ValidateGetHealthQuoteForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_health_quote_form"

    def validate_age_quote(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

      if len(slot_value)==2 and slot_value.isdigit():
        if int(slot_value)>=0 and int(slot_value)<=65:
            return {"age_quote": slot_value}
      else:
        dispatcher.utter_message("Age must be of numerica type between 0 and 65. Please enter the age again.")
        return {"age_quote": None}

    def validate_gender_quote(self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

      if slot_value=='male' or slot_value=='female':
        return {"gender_quote": slot_value}
      else:
        dispatcher.utter_message("Gender can be only male or female. Please enter the age again.")
        return {"gender_quote": None}


class ActionQuoteLife(Action):
    """Gets the status of the user's last claim."""

    def name(self) -> Text:
        """Unique identifier for the action."""
        return "action_quote_life"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        # Get the claim provided by the user.
        age = tracker.get_slot("age_quote")
        gender = tracker.get_slot("gender_quote")
        pol_term=tracker.get_slot("policy_term_quote")
        slt=["age_quote","gender_quote","policy_term_quote"]
        # Display details about the selected claims.
        if (gender=='male'):
            p=f"${str(10000+int(age)*10+int(pol_term)*100)}"
            pre_params = {
                "age": age,
                "gender": gender,
                "policy_term":pol_term,
                "premium":p
                }
            dispatcher.utter_message(template="utter_life_quote_detail", **pre_params)
            return [SlotSet(a, None) for a in slt]
        else:
            dispatcher.utter_message("the premium will be equal to 8000")
            return [SlotSet(a, None) for a in slt]
        return []

class ValidateGetLifeQuoteForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_life_quote_form"

    def validate_age_quote(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
       
       if len(slot_value)==2 and slot_value.isdigit():
        if int(slot_value)>=0 and int(slot_value)<=65:
            return {"age_quote": slot_value}
       else:
        dispatcher.utter_message("Age must be of numerica type between 0 and 65. Please enter the age again.")
        return{"age_quote": None}

    def validate_policy_term_quote(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
      if int(slot_value)%5==0 and int(slot_value)<=25:
        return {"policy_term_quote": slot_value}
      else:
        dispatcher.utter_message("Policy term must be a multiple of 5 and cannot be greater than 25 years. Please enter the policy term again.")
        return{"policy_term_quote": None}

    def validate_gender_quote(self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

      if slot_value=='male' or slot_value=='female':
        return {"gender_quote": slot_value}
      else:
        dispatcher.utter_message("Gender can be only male or female. Please enter the age again.")
        return {"gender_quote": None}

