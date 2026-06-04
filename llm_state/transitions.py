# rappresenta quali cambio di stato sono consentiti e quali no ad esempio da idle a identication è consentito
ALLOWED_TRANSITIONS = {

    "idle": [
        "identification"
    ],

    "identification": [
        "patient_identified",
        "identification_failed",
        "idle"
    ],

    "identification_failed": [
        "identification",
        "completed"
    ],

    "patient_identified": [
        "appointment_checkin",
        "completed"
    ],

    "appointment_checkin": [
        "completed",
        "error"
    ],

    "error": [
        "idle"
    ],

    "completed": [
        "idle"
    ]
}
def can_transition(current_state, new_state):

    allowed = ALLOWED_TRANSITIONS.get(current_state, [])
    return new_state in allowed

def change_mode(state, new_mode):

    if can_transition(state.current_mode, new_mode):
        print(f"Transitioning from {state.current_mode} to {new_mode}")
        state.current_mode = new_mode
        return True
    else:
        print(f"Invalid transition from {state.current_mode} to {new_mode}")
        return False