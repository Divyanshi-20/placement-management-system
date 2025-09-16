// static/js/chatbot_widget.js

function toggleChatbot() {
  const widget = document.getElementById("chatbot-widget");
  widget.style.display = widget.style.display === "flex" ? "none" : "flex";
}

async function sendChatMessage() {
  const input = document.getElementById("chatbot-input");
  const text = input.value.trim();
  if (!text) return;

  const messages = document.getElementById("chatbot-messages");
  messages.innerHTML += `<div><b>You:</b> ${text}</div>`;
  input.value = "";

 let res = await fetch('/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: userInput })
});


  let data = await res.json();
  messages.innerHTML += `<div><b>Bot:</b> ${data.answer}</div>`;
  messages.scrollTop = messages.scrollHeight;
}
