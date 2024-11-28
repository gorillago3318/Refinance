def handle_conversation(user_input, user_data):
    step = user_data.get("step", 0)
    response = ""

    # Restart functionality
    if user_input.lower() in ["restart", "start over", "reset"]:
        user_data.clear()
        user_data["step"] = 0
        response = "You have successfully restarted the conversation. How can I assist you?"
        return response, user_data

    # Step 0: Language selection
    if step == 0:
        response = {
            "text": "Welcome to Your Personal Refinancing Assistant! Please select your preferred language:",
            "buttons": [
                {"type": "reply", "reply": {"id": "lang_english", "title": "English"}},
                {"type": "reply", "reply": {"id": "lang_malay", "title": "Malay"}},
                {"type": "reply", "reply": {"id": "lang_chinese", "title": "Chinese"}}
            ]
        }
        user_data["step"] = 1

    # Step 1: Language selection
    elif step == 1:
        if user_input in ["lang_english", "lang_malay", "lang_chinese"]:
            languages = {"lang_english": "English", "lang_malay": "Malay", "lang_chinese": "Chinese"}
            user_data["language"] = languages[user_input]
            response = f"Thank you for selecting {user_data['language']}! May I know your name?"
            user_data["step"] = 2
        else:
            response = {
                "text": "Please select a valid language option by pressing one of the buttons below.",
                "buttons": [
                    {"type": "reply", "reply": {"id": "lang_english", "title": "English"}},
                    {"type": "reply", "reply": {"id": "lang_malay", "title": "Malay"}},
                    {"type": "reply", "reply": {"id": "lang_chinese", "title": "Chinese"}}
                ]
            }

    # Step 2: Collecting user name
    elif step == 2:
        user_data["name"] = user_input.title()
        response = f"Nice to meet you, {user_data['name']}! Could you please provide your age? (e.g., 27)"
        user_data["step"] = 3

    # Step 3: Collecting user age
    elif step == 3:
        if user_input.isdigit():
            user_data["age"] = int(user_input)
            response = {
                "text": f"Got it, {user_data['name']}. Is the current loan under your name only, or is it a joint loan?",
                "buttons": [
                    {"type": "reply", "reply": {"id": "individual", "title": "Individual"}},
                    {"type": "reply", "reply": {"id": "joint", "title": "Joint"}}
                ]
            }
            user_data["step"] = 4
        else:
            response = ("Please provide a valid age in numeric form.")

    # Step 4: Loan type selection (individual or joint)
    elif step == 4:
        if user_input in ["individual", "joint"]:
            user_data["loan_type"] = ("Individual" if user_input == "individual" else 
                                       "Joint")
            if user_data["loan_type"] == "Joint":
                response = ("Since it's a joint loan, could you please provide the age of the co-borrower?")
                user_data["step"] = 5
            else:
                response = ("Thank you! Could you please provide the original loan amount that you initially borrowed (in RM)?")
                user_data["step"] = 6
        else:
            response = {
                'text': ("Please specify if the loan is individual or joint."),
                'buttons': [
                    {'type': 'reply', 'reply': {'id': 'individual', 'title': 'Individual'}},
                    {'type': 'reply', 'reply': {'id': 'joint', 'title': 'Joint'}}
                ]
            }

    # Step 5: Collecting co-borrower age (for joint loans)
    elif step == 5:
        if user_input.isdigit():
            user_data["co_borrower_age"] = int(user_input)
            response = ("Thank you! Could you please provide the original loan amount that you initially borrowed (in RM)?")
            user_data["step"] = 6
        else:
            response = ("Please provide a valid age in numeric form.")

    # Step 6: Collecting original loan amount
    elif step == 6:
        if user_input.isdigit():
            user_data["loan_amount"] = int(user_input)
            response = ("Thank you! What is your current monthly payment for this loan (in RM)?")
            user_data["step"] = 7
        else:
            response = ("Please provide a valid loan amount in numeric form.")

    # Step 7: Collecting current monthly payment
    elif step == 7:
        if user_input.isdigit():
            user_data["monthly_payment"] = int(user_input)
            response = ("Great! How many years was the original loan tenure for? (e.g., 25 years)")
            user_data["step"] = 8
        else:
            response = ("Please provide a valid monthly payment in numeric form.")

    # Step 8: Collecting original loan tenure
    elif step == 8:
        if user_input.isdigit():
            user_data["original_tenure"] = int(user_input)
            response = ("Do you remember how many years are left on your loan? (Type 'Yes' or 'No')")
            user_data["step"] = 9
        else:
            response = ("Please provide a valid number of years for the original loan tenure.")

    # Step 9: Handling remaining tenure memory
    elif step == 9:
        if user_input.lower() == 'yes':
            response = ("Great! Please enter the number of years remaining on your loan.")
            user_data["step"] = 10
        elif user_input.lower() == 'no':
            response = ("No problem! Could you tell me the current interest rate on your loan? (e.g., 3.5%)")
            user_data["step"] = 11
        else:
            response = ("Please type 'Yes' or 'No' to proceed.")

    # Step 10: Collecting remaining loan tenure
    elif step == 10:
        if user_input.isdigit():
            user_data['remaining_tenure'] = int(user_input)
            response = ("Thank you! Could you tell me the current interest rate on your loan? (e.g., 3.5%)")
            user_data['step'] = 11
        else:
            response = ("Please provide a valid number of years.")

    # Step 11: Collecting interest rate
    elif step == 11:
        try:
            interest_rate = float(user_input)
            if 0 <= interest_rate <= 100:
                user_data['interest_rate'] = interest_rate
                response = ("Thank you for all the details! Let's proceed to analyze your loan information.")
                user_data['step'] = 12
            else:
                response = ("Please enter a valid interest rate (e.g., 3.5).")
        except ValueError:
            response = ("Please provide a valid interest rate in numeric form.")

    # Step 12: Analyzing data and providing insights
    elif step == 12:
        response = ("We are analyzing your data. Please hold on for a moment!")
        user_data['step'] = 13

    # Step 13: Providing calculated insights
    elif step == 13:
        response = ("Based on your provided details, here are your estimated savings and recommendations!")
        user_data['step'] = 14

    # Step 14: Closing the conversation
    elif step == 14:
        response = ("Thank you for using our assistant! If you have further questions, feel free to restart the conversation.")
        user_data['step'] = 0

    return response, user_data