from llm_state.transitions import change_mode
from llm_runtime.goals import set_goal  

def handle_event(event, state):

    if event == "Patient identified":
        change_mode(state, "patient_identified")
        print(f"\nEvent: {event} - Transitioning to patient_identified mode.")
    
    elif event == "Appointment updated":
        change_mode(state, "appointment_checkin")
        print(f"\nEvent: {event} - Transitioning to appointment_checkin mode.")
        print("\nGOAL COMPLETED") 
        set_goal( state, None )
    
    elif event == "Conversation with patient completed":
        change_mode(state, "completed")
        print(f"\nEvent: {event} - Transitioning to completed mode.")

    elif event == "tool_validation_failed":

        print(
            "\nTool validation failed. "
            "No state transition performed."
        )


    else:
        print(f"\nUnknown event: {event}")