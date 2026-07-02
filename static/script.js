const chatBox = document.getElementById("chat-box");
const questionInput = document.getElementById("question");
const MAX_TEXTAREA_HEIGHT = 160;
const sendButton = document.getElementById("send-btn");
const clearButton = document.getElementById("clear-btn");

marked.setOptions({
    breaks: true,
    gfm: true
});

function autoResizeTextarea() {
    questionInput.style.height = "auto";

    questionInput.style.height =
        Math.min(questionInput.scrollHeight, MAX_TEXTAREA_HEIGHT) + "px";
}
function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function renderUserMessage(content) {

    // Remove welcome card after first question
    const welcomeCard = chatBox.querySelector(".welcome-card");

    if (welcomeCard) {
        welcomeCard.remove();
    }

    const safeContent = escapeHtml(content);

    chatBox.insertAdjacentHTML(
        "beforeend",
        `
        <div class="message-row user">
            <div class="message-bubble">
                <div class="message-meta">You</div>
                <div class="message-text">${safeContent}</div>
            </div>
        </div>
        `
    );
}

function renderBotMessage(content, sources = [], isError = false) {
    const safeContent = marked.parse(content);
    const sourceMarkup = renderSources(sources);
    const title = isError ? "Assistant notice" : "College AI Assistant";
    const actionMarkup = isError
        ? ""
        : `
        <div class="message-actions">
            <button class="copy-btn" type="button"><i class="fa-regular fa-copy"></i> Copy</button>
        </div>
        `;

    chatBox.insertAdjacentHTML(
        "beforeend",
        `
        <div class="message-row bot">
            <div class="message-bubble">
                <div class="message-meta">${title}</div>
                <div class="message-text">${safeContent}</div>
                ${sourceMarkup}
                ${actionMarkup}
            </div>
        </div>
        `
    );
}

function renderSources(sources) {
    if (!Array.isArray(sources) || sources.length === 0) {
        return "";
    }

    const list = sources.map(source => {
        const ext = source.split('.').pop().toLowerCase();
        let iconClass = "fa-regular fa-file-lines";
        if (ext === 'pdf') {
            iconClass = "fa-regular fa-file-pdf";
        } else if (ext === 'docx' || ext === 'doc') {
            iconClass = "fa-regular fa-file-word";
        }
        return `
            <div class="source-card">
                <div class="source-icon">
                    <i class="${iconClass}"></i>
                </div>

                <div class="source-info">
                    <div class="source-name">${escapeHtml(source)}</div>
                    <div class="source-label">Knowledge Source</div>
                </div>
            </div>
        `;
    }).join("");

    return `
        <div class="sources-section">
            <div class="sources-title">
                Referenced Documents
            </div>

            <div class="sources-container">
                ${list}
            </div>
        </div>
    `;
}

function hideTyping() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom() {
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
}

function disableInput() {
    questionInput.disabled = true;
    sendButton.disabled = true;
    const icon = sendButton.querySelector("i");
    if (icon) {
        icon.className = "fa-solid fa-circle-notch fa-spin";
    }
}

function enableInput() {
    questionInput.disabled = false;
    sendButton.disabled = false;
    const icon = sendButton.querySelector("i");
    if (icon) {
        icon.className = "fa-solid fa-paper-plane";
    }
    questionInput.focus();
}

function renderWelcomeMessage() {
    chatBox.innerHTML = `
        <div class="welcome-card">
            <h2>Welcome to your university AI portal</h2>
            <p>Ask about admissions, fees, hostels, placements, transport, library services, and campus information. The assistant responds with grounded guidance and source references.</p>
            <div class="quick-prompts">
                <button class="quick-chip" type="button">What are the hostel fees?</button>
                <button class="quick-chip" type="button">How do I apply for admission?</button>
                <button class="quick-chip" type="button">What placements are available?</button>
            </div>
        </div>
    `;
}

function showTyping() {
    chatBox.insertAdjacentHTML(
        "beforeend",
        `
        <div class="message-row bot" id="typing-indicator">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
        `
    );

    scrollToBottom();
}

async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question || questionInput.disabled) {
        return;
    }

   renderUserMessage(question);

questionInput.value = "";
questionInput.style.height = "auto";

disableInput();
showTyping();
scrollToBottom();

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json().catch(() => ({}));
        hideTyping();

        if (!response.ok || !data || typeof data.answer !== "string") {
            renderBotMessage("The assistant could not complete that request. Please try again in a moment.", [], true);
        } else {
            renderBotMessage(data.answer, Array.isArray(data.sources) ? data.sources : []);
        }
    } catch (error) {
        hideTyping();
        renderBotMessage("The assistant is temporarily unavailable. Please try again shortly.", [], true);
    } finally {
        enableInput();
        scrollToBottom();
    }
}

function clearChat() {
    renderWelcomeMessage();
    scrollToBottom();
}

questionInput.addEventListener("input", autoResizeTextarea);

sendButton.addEventListener("click", askQuestion);
clearButton.addEventListener("click", clearChat);

questionInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

chatBox.addEventListener("click", function (event) {
    const chip = event.target.closest(".quick-chip");
    if (chip) {
        questionInput.value = chip.textContent.trim();
        askQuestion();
        return;
    }

    const copyButton = event.target.closest(".copy-btn");
    if (!copyButton) {
        return;
    }

    const bubble = copyButton.closest(".message-bubble");
    const messageText = bubble ? bubble.querySelector(".message-text").textContent : "";

    navigator.clipboard.writeText(messageText).then(() => {
        copyButton.innerHTML = `<i class="fa-solid fa-check"></i> Copied`;
        copyButton.classList.add("copied");
        window.setTimeout(() => {
            copyButton.innerHTML = `<i class="fa-regular fa-copy"></i> Copy`;
            copyButton.classList.remove("copied");
        }, 1400);
    });
});

clearChat();
autoResizeTextarea();