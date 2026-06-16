const video = document.getElementById("video");

navigator.mediaDevices
    .getUserMedia({
        video: true
    })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error(err);
    });

const identifyBtn =
    document.getElementById("identifyBtn");

identifyBtn.addEventListener(
    "click",
    async () => {

        console.log("Riconosci Paziente premuto");

        const canvas =
            document.createElement("canvas");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx =
            canvas.getContext("2d");

        ctx.drawImage(
            video,
            0,
            0
        );

        const blob =
            await new Promise(
                resolve =>
                    canvas.toBlob(
                        resolve,
                        "image/jpeg"
                    )
            );

        const formData =
            new FormData();

        formData.append(
            "file",
            blob,
            "frame.jpg"
        );

        const response =
            await fetch(
                "/identify",
                {
                    method: "POST",
                    body: formData
                }
            );

        const result =
            await response.json();

        console.log(result);

        const resultDiv =
        document.getElementById("result");

        if (result.patient_id) {

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-check"></i>
                    Paziente riconosciuto
                </h2>
                <p><strong>ID Paziente:</strong> ${result.patient_id}</p>
                <p><strong>Confidenza:</strong> ${(result.score * 100).toFixed(1)}%</p>
            `;

        } else {

            resultDiv.innerHTML = `
                <h2>
                    <i class="fa-solid fa-circle-xmark"></i>
                    Paziente non riconosciuto
                </h2>
                <p>Confidenza: ${(result.score * 100).toFixed(1)}%</p>
            `;
        }
        }
);