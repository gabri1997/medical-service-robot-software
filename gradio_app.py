import gradio
from main import identify_patient
from fetch_api_patient_data import execute_fetch_and_update

patient_id = None

def identify():
        global patient_id
        result = identify_patient()
        if isinstance(result, dict):
            return f"Error: {result['event']}"
        patient_id = result
        return f"Patient identified: {patient_id}"

def check_in():
    global patient_id
    if patient_id is None:
        return "No patient identified yet. Please start the identification process first."
    result = execute_fetch_and_update(patient_id)
    if result["success"]:
        # qui devo ritornarlo formattato cosi visto che il backend ritorna un dizionario
        return (
            f"Check-in completed.\n"
            f"Status: {result['data']['new_status']}\n"
            f"Timing: {result['data']['timing']}"
        )

    return f"Error: {result['event']}"

def reset():
    global patient_id
    patient_id = None
    return "Session reset."

with gradio.Blocks(title="Medical Service Robot") as demo:
    gradio.Markdown("## Medical Service Robot Interface")
    status = gradio.Textbox(label="Identified Patient ID")
    identify_button = gradio.Button("Identify Patient")
    checkin_button = gradio.Button("Check-in Patient")
    identify_button.click(identify, outputs=status)
    checkin_button.click(check_in, outputs=status)
    reset_button = gradio.Button("Reset Session")
    reset_button.click(reset, outputs=status)

demo.launch()