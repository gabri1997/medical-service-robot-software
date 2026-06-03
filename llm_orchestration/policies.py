
def validate_tool_call(function_name, state):

    if (function_name == "llm_execute_fetch_and_update" and state.patient_id is None):

        return False, "Patient not identified"
    
    if (function_name == "llm_execute_fetch_and_update"and state.current_goal != "check_patient_appointment"):

        return False, "Current goal does not allow appointment retrieval"


    if (function_name == "llm_identify_patient" and state.patient_id is not None):

        return False, "Patient already identified"

    return True, None

