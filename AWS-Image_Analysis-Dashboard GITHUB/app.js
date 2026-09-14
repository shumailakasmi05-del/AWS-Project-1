// Replace this with your deployed API Gateway endpoint.
const API_URL = "YOUR_API_GATEWAY_URL";


async function uploadImage() {

    const fileInput =
        document.getElementById("imageFile");

    const file =
        fileInput.files[0];

    const loading =
        document.getElementById("loading");

    const error =
        document.getElementById("error");

    const dashboard =
        document.getElementById("dashboard");


    if (!file) {

        error.textContent =
            "Please choose an image first.";

        error.classList.remove("hidden");

        return;
    }


    dashboard.classList.add("hidden");

    error.classList.add("hidden");

    loading.textContent =
        "Uploading image...";

    loading.classList.remove("hidden");


    try {

        // Get a secure S3 upload URL

        const urlResponse = await fetch(
            `${API_URL}/upload`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    filename: file.name
                })
            }
        );


        const uploadData =
            await urlResponse.json();


        if (!urlResponse.ok) {

            throw new Error(
                uploadData.error ||
                "Could not create upload URL."
            );
        }


        // Upload image directly to S3

        loading.textContent =
            "Uploading image to S3...";


        const s3Response = await fetch(
            uploadData.upload_url,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/octet-stream"
                },

                body: file
            }
        );


        if (!s3Response.ok) {

            throw new Error(
                "Image upload to S3 failed."
            );
        }


        // Wait for the S3 → Lambda pipeline

        loading.textContent =
            "Image uploaded. AWS is analyzing it...";


        await waitForAnalysis(
            uploadData.filename
        );


    } catch (err) {

        console.error(err);

        error.textContent =
            "Error: " + err.message;

        error.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");

    }

}


async function waitForAnalysis(filename) {

    const maxAttempts = 30;


    for (
        let attempt = 0;
        attempt < maxAttempts;
        attempt++
    ) {

        try {

            const response = await fetch(
                `${API_URL}/analysis?file=${encodeURIComponent(filename)}`
            );


            if (response.ok) {

                const data =
                    await response.json();

                displayResults(data);

                return;
            }

        } catch (error) {

            console.log(
                "Waiting for analysis..."
            );

        }


        await new Promise(
            resolve =>
                setTimeout(resolve, 2000)
        );

    }


    throw new Error(
        "Analysis is taking longer than expected."
    );

}


function displayResults(data) {

    document
        .getElementById("dashboard")
        .classList.remove("hidden");


    document.getElementById("imageName").textContent =
        data.image?.file_name ||
        "Image";


    document.getElementById("summary").textContent =
        data.summary?.description ||
        "No AI summary available.";


    document.getElementById("objectCount").textContent =
        data.objects?.count ||
        0;


    document.getElementById("faceCount").textContent =
        data.faces?.count ||
        0;


    document.getElementById("textCount").textContent =
        data.text?.items?.length ||
        0;


    document.getElementById("safetyStatus").textContent =
        data.safety?.status ||
        "Unknown";


    displayObjects(data.objects);

    displayFaces(data.faces);

    displayText(data.text);

    displaySafety(data.safety);

}


function displayObjects(objects) {

    const container =
        document.getElementById("objects");

    container.innerHTML = "";


    if (!objects?.detected?.length) {

        container.innerHTML =
            "<p>No objects detected.</p>";

        return;
    }


    objects.detected.forEach(object => {

        const item =
            document.createElement("div");

        item.className =
            "data-item";


        item.innerHTML = `
            <span>${object.name}</span>
            <span class="confidence">
                ${object.confidence}%
            </span>
        `;


        container.appendChild(item);

    });

}


function displayFaces(faces) {

    const container =
        document.getElementById("faces");

    container.innerHTML = "";


    if (!faces?.detected?.length) {

        container.innerHTML =
            "<p>No faces detected.</p>";

        return;
    }


    faces.detected.forEach(face => {

        const emotion =
            face.strongest_emotion?.emotion ||
            "Unknown";


        const item =
            document.createElement("div");

        item.className =
            "data-item";


        item.innerHTML = `
            <span>
                Face ${face.face_id}
            </span>

            <span>
                ${emotion}
            </span>
        `;


        container.appendChild(item);

    });

}


function displayText(text) {

    const container =
        document.getElementById("text");

    container.innerHTML = "";


    if (!text?.items?.length) {

        container.innerHTML =
            "<p>No text detected.</p>";

        return;
    }


    text.items.forEach(item => {

        const row =
            document.createElement("div");

        row.className =
            "data-item";


        row.innerHTML = `
            <span>${item.text}</span>
            <span class="confidence">
                ${item.confidence}%
            </span>
        `;


        container.appendChild(row);

    });

}


function displaySafety(safety) {

    const container =
        document.getElementById("safety");

    container.innerHTML = "";


    if (!safety) {

        container.innerHTML =
            "<p>No safety information available.</p>";

        return;
    }


    const status =
        document.createElement("div");

    status.className =
        "data-item";


    status.innerHTML = `
        <span>Status</span>
        <strong>${safety.status}</strong>
    `;


    container.appendChild(status);


    if (safety.issues?.length) {

        safety.issues.forEach(issue => {

            const item =
                document.createElement("div");

            item.className =
                "data-item";


            item.innerHTML = `
                <span>${issue.name}</span>
                <span class="confidence">
                    ${issue.confidence}%
                </span>
            `;


            container.appendChild(item);

        });

    }

}