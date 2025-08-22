document.addEventListener("DOMContentLoaded", () => {
  const chatToggle = document.getElementById("chat-toggle");
  const chatWidget = document.getElementById("chat-widget");
  const closeBtn = document.querySelector(".close-btn");
  const sendBtn = document.getElementById("send-btn");
  const chatInput = document.getElementById("user-input");
  const messages = document.getElementById("messages");
  const languageSelector = document.getElementById("language");

  const greetings = {
    en: "👋 Hello! I am your Cybercrime Assistant. How can I help you today?",
    hi: "👋 नमस्ते! मैं आपका साइबरक्राइम सहायक हूँ। मैं आपकी कैसे मदद कर सकता हूँ?",
    te: "👋 హలో! నేను మీ సైబర్ క్రైమ్ సహాయకుని. నేను మీకు ఎలా సహాయం చేయగలను?",
    ta: "👋 வணக்கம்! நான் உங்கள் சைபர் குற்ற உதவியாளர். நான் உங்களுக்கு எப்படி உதவலாம்?",
    kn: "👋 ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಸೈಬರ್ ಅಪರಾಧ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    ml: "👋 ഹലോ! ഞാൻ നിങ്ങളുടെ സൈബർ കുറ്റാന്വേഷണ സഹായി. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
    mr: "👋 नमस्कार! मी तुमचा सायबरक्राइम सहाय्यक आहे. मी तुम्हाला कशी मदत करू शकतो?",
    gu: "👋 નમસ્તે! હું તમારો સાયબરક્રાઇમ સહાયક છું. હું તમને કેવી રીતે મદદ કરી શકું?"
  };

  function addMessage(message, sender = "bot") {
    const msgDiv = document.createElement("div");
    msgDiv.className = sender === "bot" ? "bot-msg" : "user-msg";
    msgDiv.textContent = message;
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
  }

  function showGreeting() {
    const lang = languageSelector.value;
    addMessage(greetings[lang], "bot");
  }

  chatToggle.addEventListener("click", () => {
    chatWidget.style.display = "block";
    chatToggle.style.display = "none";
    messages.innerHTML = "";
    showGreeting();
  });

  closeBtn.addEventListener("click", () => {
    chatWidget.style.display = "none";
    chatToggle.style.display = "block";
  });

  sendBtn.addEventListener("click", () => {
    const text = chatInput.value.trim();
    if (text) {
      addMessage(text, "user");
      chatInput.value = "";
      setTimeout(() => {
        addMessage("✅ Got it! I will process your request.", "bot");
      }, 1000);
    }
  });

  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendBtn.click();
    }
  });

  languageSelector.addEventListener("change", () => {
    messages.innerHTML = "";
    showGreeting();
  });
});
