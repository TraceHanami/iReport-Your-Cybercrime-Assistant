function toggleChat() {
  let chat = document.getElementById("chat-widget");
  chat.style.display = (chat.style.display === "none" || chat.style.display === "") 
    ? "block" 
    : "none";
}

function sendMessage() {
  let input = document.getElementById("userInput");
  let msg = input.value.trim();
  if (msg === "") return;

  let messages = document.getElementById("messages");

  let userDiv = document.createElement("div");
  userDiv.className = "user-msg";
  userDiv.textContent = msg;
  messages.appendChild(userDiv);

  let botDiv = document.createElement("div");
  botDiv.className = "bot-msg";

  if(msg.toLowerCase().includes("offerings")){
    botDiv.textContent = "We help with cybercrime reporting, awareness, and resources.";
  } 
  else if(msg.toLowerCase().includes("issue")){
    botDiv.textContent = "Please describe your issue and we'll guide you.";
  } 
  else if(msg.toLowerCase().includes("report")){
    botDiv.textContent = "You can file a cybercrime report directly through the iReport portal.";
  } 
  else {
    botDiv.textContent = "I'm here to assist! Try asking about offerings, issues, or how to report.";
  }

  messages.appendChild(botDiv);

  messages.scrollTop = messages.scrollHeight;
  input.value = "";
}
