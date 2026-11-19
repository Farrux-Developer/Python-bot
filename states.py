"""Finite State Machine (FSM) states for telebot."""

from telebot.handler_backends import State, StatesGroup


class OrderQuiz(StatesGroup):
    """FSM states for the website ordering questionnaire."""
    select_service = State()        # Step 1: Select website category
    input_description = State()     # Step 1 cont.: Task description or reference link
    select_options = State()        # Step 2: Interactive multi-toggle options (✅/⬜)
    select_budget = State()         # Step 3: Choose budget tier or auto-calculation
    input_custom_budget = State()  # Step 3 cont.: Custom budget text entry
    input_contact = State()         # Step 4: Contact info input
    confirm_order = State()         # Step 5: Order review & confirmation


class AdminState(StatesGroup):
    """FSM states for administrator actions."""
    reply_message = State()         # Admin composing a direct message to a client
