const video             = document.getElementById("video");
const loading           = document.getElementById("loading");
const resultDiv         = document.getElementById("result");
const checkinBtn        = document.getElementById("checkinBtn");
const identifyBtn       = document.getElementById("identifyBtn");
const startRecordingBtn = document.getElementById("startRecordingBtn");
const voiceSection      = document.getElementById("voiceSection");

// ─── Stato iniziale ───────────────────────────────────────────────────────────
checkinBtn.style.display = "none";
voiceSection.style.display = "none";

let mediaRecorder    = null;
let audioChunks      = [];
let recordingTimeout = null;

// ─────────────────────────────────────────
// ACCESSO ALLA TELECAMERA
// ─────────────────────────────────────────
navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error(err);
        showError(resultDiv, "Impossibile accedere alla telecamera");
    });

// ─────────────────────────────────────────
// RICONOSCIMENTO PAZIENTE (VOLTO)
// ─────────────────────────────────────────
identifyBtn.addEventListener("click", async () => {

    if (!video.videoWidth || !video.videoHeight) {
        resultDiv.innerHTML = `
            <h2><i class="fa-solid fa-circle-xmark"></i> Telecamera non ancora pronta</h2>
            <p>Attendi qualche secondo e riprova.</p>
        `;
        return;
    }

    // Reset UI
    resetCheckin();
    showLoading("Analisi del volto in corso...");

    try {
        const canvas = document.createElement("canvas");
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);

        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));

        const formData = new FormData();
        formData.append("file", blob, "frame.jpg");

        const response = await fetch("/identify", { method: "POST", body: formData });
        const result   = await response.json();
        console.log(result);

        if (result.patient_id) {
            showCheckinBtn();
            voiceSection.style.display = "none";
            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-check"></i> Paziente riconosciuto</h2>
                <p>
                    <strong>ID Paziente:</strong> ${result.patient_id}
                    ${result.name    ? `<br><strong>Nome:</strong> ${result.name}`       : ""}
                    ${result.surname ? `<br><strong>Cognome:</strong> ${result.surname}` : ""}
                </p>
                <p><strong>Confidenza:</strong> ${(result.score * 100).toFixed(1)}%</p>
            `;
        } else {
            voiceSection.style.display = "block";
            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-xmark"></i> Paziente non riconosciuto tramite volto</h2>
                <p>Prova il riconoscimento vocale.</p>
            `;
        }

    } catch (error) {
        console.error(error);
        showError(resultDiv, "Errore durante il riconoscimento");
    } finally {
        hideLoading();
    }
});

// ─────────────────────────────────────────
// CHECK-IN
// ─────────────────────────────────────────
checkinBtn.addEventListener("click", async () => {

    showLoading("Registrazione del check-in...");

    try {
        const response = await fetch("/checkin", { method: "POST" });
        const result   = await response.json();
        console.log(result);

        if (result.success) {
            checkinBtn.style.display = "none";

            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-check"></i> Check-in completato</h2>
                <p>
                    <strong>Paziente:</strong> ${result.data.name} ${result.data.surname}
                </p>
                <p><strong>Stato:</strong> ${result.data.new_status}</p>
                <p><strong>Orario:</strong> ${result.data.timing}</p>
                <div style="
                    margin-top: 20px;
                    padding: 20px;
                    background: #dcfce7;
                    border: 2px solid #89f0af;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                ">
                    Può accomodarsi nella sala di attesa.
                </div>
            `;

            setTimeout(() => resetAll(), 6000);

        } else {
            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-xmark"></i> Operazione non completata</h2>
                <p>${result.message || "Il paziente non ha appuntamenti oggi."}</p>
            `;
        }

    } catch (error) {
        console.error(error);
        showError(resultDiv, "Errore durante il check-in");
    } finally {
        hideLoading();
    }
});

// ─────────────────────────────────────────
// RICONOSCIMENTO VOCALE
// ─────────────────────────────────────────
startRecordingBtn.addEventListener("click", async () => {

    if (mediaRecorder && mediaRecorder.state === "recording") return;

    if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        recordingTimeout = null;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        audioChunks  = [];
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            stream.getTracks().forEach(t => t.stop());
            await sendAudioToBackend(audioBlob);
        };

        mediaRecorder.start();

        startRecordingBtn.disabled = true;
        startRecordingBtn.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Registrazione in corso...
        `;

        recordingTimeout = setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }
            startRecordingBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Invio audio...
            `;
        }, 3000);

    } catch (error) {
        console.error(error);
        resetRecordingBtn();
        showError(resultDiv, "Impossibile accedere al microfono");
    }
});

async function sendAudioToBackend(audioBlob) {

    showLoading("Elaborazione audio...");

    try {
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm");

        const response = await fetch("/voice-identify", { method: "POST", body: formData });
        const result   = await response.json();
        console.log(result);

        if (result.patient_id) {
            showCheckinBtn();
            voiceSection.style.display = "none";
            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-check"></i> Paziente riconosciuto tramite voce</h2>
                <p>
                    <strong>ID Paziente:</strong> ${result.patient_id}
                    ${result.name    ? `<br><strong>Nome:</strong> ${result.name}`       : ""}
                    ${result.surname ? `<br><strong>Cognome:</strong> ${result.surname}` : ""}
                </p>
            `;
        } else {
            resultDiv.innerHTML = `
                <h2><i class="fa-solid fa-circle-xmark"></i> Paziente non riconosciuto</h2>
                <p>Nessuna corrispondenza trovata. Riprova o contatta il personale.</p>
            `;
            const popup =
                document.getElementById(
                    "warningPopup"
                );

            popup.classList.add("show");

            setTimeout(() => {
                popup.classList.remove("show");
            }, 6000);
                    }

    } catch (error) {
        console.error(error);
        showError(resultDiv, "Errore durante il riconoscimento vocale");
    } finally {
        hideLoading();
        resetRecordingBtn();
    }
}

// ─────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────
function showLoading(msg) {
    loading.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${msg}`;
    loading.className = "loading-visible";
}

function hideLoading() {
    loading.className = "loading-hidden";
}

function showCheckinBtn() {
    checkinBtn.style.display = "flex";
}

function showError(container, msg) {
    container.innerHTML = `<h2><i class="fa-solid fa-circle-xmark"></i> ${msg}</h2>`;
}

function resetRecordingBtn() {
    startRecordingBtn.disabled = false;
    startRecordingBtn.innerHTML = `
        <i class="fa-solid fa-microphone"></i>
        Avvia registrazione
    `;
}

function resetCheckin() {
    checkinBtn.style.display = "none";
    voiceSection.style.display = "none";
}

function resetAll() {
    resultDiv.innerHTML   = "Nessun paziente identificato";
    checkinBtn.style.display = "none";
    voiceSection.style.display = "none";
}