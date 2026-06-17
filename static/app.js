const video = document.getElementById("video");
const loading = document.getElementById("loading");
const resultDiv = document.getElementById("result");

// Dichiarazione anticipata per evitare problemi di riferimento
const checkinBtn = document.getElementById("checkinBtn");
const identifyBtn = document.getElementById("identifyBtn");
const startRecordingBtn = document.getElementById("startRecordingBtn");

checkinBtn.disabled = true;

// Nascondo la sezione vocale all'avvio
document.getElementById("voiceSection").style.display = "none";

// Variabile per gestire il timeout della registrazione
let recordingTimeout = null;
let mediaRecorder = null;
let audioChunks = [];

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
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Impossibile accedere alla telecamera
            </h2>
        `;
    });

// ─────────────────────────────────────────
// RICONOSCIMENTO PAZIENTE (VOLTO)
// ─────────────────────────────────────────
identifyBtn.addEventListener("click", async () => {

    // Controllo che la telecamera sia pronta
    if (!video.videoWidth || !video.videoHeight) {
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Telecamera non ancora pronta
            </h2>
            <p>Attendi qualche secondo e riprova.</p>
        `;
        return;
    }

    loading.innerHTML = `
        <i class="fa-solid fa-spinner fa-spin"></i>
        Analisi del volto in corso...
    `;
    loading.className = "loading-visible";

    try {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);

        const blob = await new Promise(resolve =>
            canvas.toBlob(resolve, "image/jpeg")
        );

        const formData = new FormData();
        formData.append("file", blob, "frame.jpg");

        const response = await fetch("/identify", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        console.log(result);

        if (result.patient_id) {
            checkinBtn.disabled = false;

            document.getElementById("voiceSection").style.display = "none";

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-check"></i>
                    Paziente riconosciuto
                </h2>
                <p>
                    <strong>ID Paziente:</strong> ${result.patient_id}
                    ${result.name ? `<br><strong>Nome:</strong> ${result.name}` : ""}
                    ${result.surname ? `<br><strong>Cognome:</strong> ${result.surname}` : ""}
                </p>
                <p>
                    <strong>Confidenza:</strong>
                    ${(result.score * 100).toFixed(1)}%
                </p>
            `;
        } else {
            checkinBtn.disabled = true;

            document.getElementById("voiceSection").style.display = "block";

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-xmark"></i>
                    Paziente non riconosciuto tramite volto
                </h2>
                <p>Prova il riconoscimento vocale.</p>
            `;
        }

    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Errore durante il riconoscimento
            </h2>
        `;
    } finally {
        loading.className = "loading-hidden";
    }
});

// ─────────────────────────────────────────
// CHECK-IN
// ─────────────────────────────────────────
checkinBtn.addEventListener("click", async () => {

    loading.innerHTML = `
        <i class="fa-solid fa-spinner fa-spin"></i>
        Registrazione del check-in...
    `;
    loading.className = "loading-visible";

    try {
        const response = await fetch("/checkin", { method: "POST" });
        const result = await response.json();
        console.log(result);

        if (result.success) {
            checkinBtn.disabled = true;

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-check"></i>
                    Check-in completato
                </h2>
                <p>
                    <strong>Paziente:</strong>
                    ${result.data.name} ${result.data.surname}
                </p>
                <p>
                    <strong>Stato:</strong> ${result.data.new_status}
                </p>
                <p>
                    <strong>Orario:</strong> ${result.data.timing}
                </p>
                <div id="waitingRoomMessage" style="
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

            setTimeout(() => {
                resultDiv.innerHTML = "";
                checkinBtn.disabled = true;
                document.getElementById("voiceSection").style.display = "none";
            }, 6000);

        } else {
            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-xmark"></i>
                    Operazione non completata
                </h2>
                <p>${result.message || "Il paziente non ha appuntamenti oggi."}</p>
            `;
        }

    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Errore durante il check-in
            </h2>
        `;
    } finally {
        loading.className = "loading-hidden";
    }
});

// ─────────────────────────────────────────
// RICONOSCIMENTO VOCALE
// ─────────────────────────────────────────
startRecordingBtn.addEventListener("click", async () => {

    // Evita doppio click durante la registrazione
    if (mediaRecorder && mediaRecorder.state === "recording") return;

    // Cancella eventuale timeout precedente rimasto in sospeso
    if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        recordingTimeout = null;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            stream.getTracks().forEach(track => track.stop());
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
        }, 5000);

    } catch (error) {
        console.error(error);
        startRecordingBtn.disabled = false;
        startRecordingBtn.innerHTML = `
            <i class="fa-solid fa-microphone"></i>
            Avvia registrazione
        `;
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Impossibile accedere al microfono
            </h2>
        `;
    }
});

async function sendAudioToBackend(audioBlob) {

    loading.innerHTML = `
        <i class="fa-solid fa-spinner fa-spin"></i>
        Elaborazione audio...
    `;
    loading.className = "loading-visible";

    try {
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm");

        const response = await fetch("/voice-identify", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        console.log(result);

        if (result.patient_id) {
            checkinBtn.disabled = false;

            document.getElementById("voiceSection").style.display = "none";

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-check"></i>
                    Paziente riconosciuto tramite voce
                </h2>
                <p>
                    <strong>ID Paziente:</strong> ${result.patient_id}
                    ${result.name ? `<br><strong>Nome:</strong> ${result.name}` : ""}
                    ${result.surname ? `<br><strong>Cognome:</strong> ${result.surname}` : ""}
                </p>
            `;
        } else {
            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-xmark"></i>
                    Paziente non riconosciuto
                </h2>
                <p>Nessuna corrispondenza trovata. Riprova o contatta il personale.</p>
            `;
        }

    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `
            <h2>
                <i class="fa-solid fa-circle-xmark"></i>
                Errore durante il riconoscimento vocale
            </h2>
        `;
    } finally {
        loading.className = "loading-hidden";

        // Reset bottone registrazione sempre nel finally
        startRecordingBtn.disabled = false;
        startRecordingBtn.innerHTML = `
            <i class="fa-solid fa-microphone"></i>
            Avvia registrazione
        `;
    }
}