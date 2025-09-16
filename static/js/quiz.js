function loadQuiz(type) {
  const questions = quizQuestions[type];
  const quizForm = document.getElementById("quiz-form");
  const quizResult = document.getElementById("quiz-result");
  const submitBtn = document.getElementById("submit-quiz");

  quizForm.innerHTML = questions.map((q, i) => `
    <div class="p-4 bg-white rounded-lg shadow">
      <p class="font-medium mb-2">Q${i + 1}. ${q.q}</p>
      ${q.options.map(opt => `
        <label class="block">
          <input type="radio" name="q${i}" value="${opt}" class="mr-2"> ${opt}
        </label>`).join("")}
    </div>
  `).join("");

  quizResult.classList.add("hidden");
  submitBtn.classList.remove("hidden");

  submitBtn.onclick = (e) => {
    e.preventDefault();
    let score = 0;
    let feedback = "";

    questions.forEach((q, i) => {
      const selected = quizForm.querySelector(`input[name="q${i}"]:checked`);
      if (selected) {
        if (selected.value === q.answer) {
          score++;
          feedback += `<p class="text-green-600">✔ Q${i + 1}: Correct</p>`;
        } else {
          feedback += `<p class="text-red-600">✘ Q${i + 1}: Wrong (Correct: ${q.answer})</p>`;
        }
      } else {
        feedback += `<p class="text-yellow-600">⚠ Q${i + 1}: Not Answered (Correct: ${q.answer})</p>`;
      }
    });

    quizResult.innerHTML = `
      <h4 class="font-bold mb-2">Your Score: ${score} / ${questions.length}</h4>
      <div class="space-y-1">${feedback}</div>
    `;
    quizResult.classList.remove("hidden");
  };
}
