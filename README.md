## Description

This project explores the use of robotics in healthcare to improve patient experience and streamline check-in procedures. It focuses on developing software for a robot that welcomes patients, assists with identification, and retrieves appointment data.

The system is designed as a modular pipeline combining perception, decision-making, and interaction components. Facial recognition is used as the primary identification method, generating identity predictions with confidence scores. When visual identification is uncertain or ambiguous, the system falls back to voice interaction, using Speech-to-Text to capture the patient's name.

The transcribed input is normalized and matched against a local database using similarity metrics (e.g., Levenshtein distance) to retrieve candidate identities. If multiple candidates are found, facial recognition is used again to disambiguate. Once the correct `patient_id` is determined, the system queries external healthcare APIs to retrieve appointments and patient data.

A decision engine then classifies the situation (e.g., on-time, late, or new patient) and determines the appropriate response. Interaction with the patient is handled through Speech-to-Text and Text-to-Speech modules, with optional support from Large Language Models to enhance dialogue quality.

---

## Operational Flow

1. The patient arrives at the system.  
2. Face recognition is attempted.  
3. If the face is recognized with high confidence, the corresponding `patient_id` is retrieved.  
4. If the face is not recognized or multiple candidates are detected, the system asks for the patient’s name and surname.  
5. The spoken input is transcribed into text.  
6. The text is normalized to a consistent format.  
7. The system searches the local database using a similarity metric (e.g., Levenshtein distance).  
8. One or more candidate patients are retrieved.  
9. If necessary, face recognition is used again to disambiguate between candidates.  
10. Once the correct `patient_id` is identified, an API call is made to retrieve the patient’s appointments.

![Diagramma](assets/chart.png)

# LLM-Based Decision Making and Agent Runtime

In this component of the project, the objective is to leverage OpenAI's ChatGPT API as the decision-making layer of the medical service robot. Rather than hard-coding all possible conversational flows, the Large Language Model (LLM) is responsible for understanding user requests, reasoning about the current context, and selecting the most appropriate action to perform.

The interaction begins with a user message, which is appended to the conversation history maintained by the system. Based on the user's request, the software infers the robot's current goal (e.g., checking a patient's appointment) and initializes an iterative reasoning loop.

A maximum number of iterations is defined (currently 5) to prevent infinite execution cycles. During each iteration, a request is sent to the LLM together with the list of tools available to the robot. By using `tool_choice="auto"`, the model is allowed to autonomously decide whether a tool should be called and which specific tool best satisfies the current objective.

After receiving the LLM response, the system extracts any tool calls proposed by the model. For each requested tool invocation, the corresponding function name and arguments are parsed and validated before execution.

A dedicated policy layer verifies whether the requested action is allowed according to the robot's current runtime state and active goal. This prevents invalid or unsafe actions from being executed. Examples include preventing appointment retrieval before patient identification has been completed or blocking actions that are inconsistent with the current task.

If the validation succeeds, the request is forwarded to the dispatcher. The dispatcher acts as an orchestration layer that maps the tool selected by the LLM to the corresponding backend functionality. The dispatcher invokes the appropriate wrapper, which in turn calls the deterministic backend logic responsible for executing the requested action (e.g., patient identification, appointment retrieval, appointment status update, database access, or notification generation).

The backend returns its output as a structured JSON object. In addition to the action result, the response contains a semantic event describing the outcome of the operation. Examples include:

* `patient_identified`
* `appointment_updated`
* `tool_validation_failed`

These events are processed by an event handler responsible for managing the robot's runtime state. The event handler evaluates whether a state transition is valid according to the predefined state machine and updates the robot's operating mode accordingly.

The architecture currently maintains both a conversational memory and a structured runtime state:

* **Conversational memory** stores the full message history exchanged between the user, the LLM, and the tools.
* **Runtime state** stores structured information such as:

  * patient identifier
  * appointment information
  * current operating mode
  * active goal
  * session status

A key component of the system is **Observation Injection**. After a tool has been executed, its result is appended to the conversation as a tool message. This allows the LLM to observe the outcome of its previous action and reason on updated information during the next iteration.

The overall execution cycle can be summarized as:

User Input
→ LLM Reasoning
→ Tool Selection
→ Policy Validation
→ Dispatcher
→ Backend Execution
→ Event Generation
→ State Update
→ Observation Injection
→ LLM Re-Reasoning

This approach enables the robot to operate as a stateful conversational agent capable of reasoning over its own actions, maintaining context across multiple interactions, and dynamically adapting its behavior based on both user input and runtime events.
