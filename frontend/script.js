const textInput = document.getElementById("textInput");
const predictBtn = document.getElementById("predictBtn");
const conversation = document.getElementById("conversation");
const charCount = document.getElementById("charCount");
const newChatBtn = document.getElementById("newChatBtn");
const exampleBtn = document.querySelector(".example-btn");


// Character counter
textInput.addEventListener("input", () => {
    charCount.textContent = `${textInput.value.length} characters`;
});


// Predict button
predictBtn.addEventListener("click", predictNextWord);


// Ctrl + Enter
textInput.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "Enter") {
        predictNextWord();
    }
});


// Example sentence
if (exampleBtn) {
    exampleBtn.addEventListener("click", () => {
        textInput.value = "I love";
        textInput.focus();
        charCount.textContent = `${textInput.value.length} characters`;
    });
}


// Clear current prediction
newChatBtn.addEventListener("click", () => {
    conversation.innerHTML = `
        <div class="empty-state" id="emptyState">
            <div class="neural-icon">
                <span></span><span></span><span></span>
            </div>
            <h3>Ready for your sentence</h3>
            <p>Try something like <button class="example-btn">"I love"</button></p>
        </div>
    `;

    textInput.value = "";
    charCount.textContent = "0 characters";

    const newExampleBtn = conversation.querySelector(".example-btn");

    newExampleBtn.addEventListener("click", () => {
        textInput.value = "I love";
        textInput.focus();
        charCount.textContent = `${textInput.value.length} characters`;
    });
});


async function predictNextWord() {

    const text = textInput.value.trim();

    if (!text) {
        showError("Please enter a sentence first.");
        return;
    }

    predictBtn.disabled = true;
    predictBtn.querySelector("span:first-child").textContent = "Predicting...";

    try {

        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }


        // DOM manipulation:
        // Add the user's sentence and model's response to the UI.
        renderPrediction(data);


    } catch (error) {

        console.error(error);
        showError(
            error.message === "Failed to fetch"
                ? "Backend server is not running. Start Flask first."
                : error.message
        );

    } finally {

        predictBtn.disabled = false;
        predictBtn.querySelector("span:first-child").textContent = "Predict";
    }
}


function renderPrediction(data) {

    const emptyState = document.getElementById("emptyState");

    if (emptyState) {
        emptyState.remove();
    }


    conversation.insertAdjacentHTML("beforeend", `
        <div class="message user">
            <div class="message-label">YOU</div>
            <div class="message-body">
                <div class="message-type">Input sentence</div>
                <div class="message-text">${escapeHtml(data.input)}</div>
            </div>
        </div>

        <div class="message ai">
            <div class="message-label">AI</div>
            <div class="message-body">
                <div class="message-type">RNN prediction</div>
                <div class="message-text">
                    ${escapeHtml(data.input)}
                    <strong>${escapeHtml(data.next_word)}</strong>
                </div>
            </div>
        </div>
    `);

    conversation.scrollTop = conversation.scrollHeight;
}


function showError(message) {

    const emptyState = document.getElementById("emptyState");

    if (emptyState) {
        emptyState.remove();
    }

    conversation.insertAdjacentHTML("beforeend", `
        <div class="message ai">
            <div class="message-label">!</div>
            <div class="message-body">
                <div class="message-type">Error</div>
                <div class="message-text">${escapeHtml(message)}</div>
            </div>
        </div>
    `);
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
