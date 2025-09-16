document.addEventListener("DOMContentLoaded", () => {
  const practiceDiv = document.getElementById("practice-questions");
  const categoryButtons = document.getElementById("category-buttons");
  const practiceSection = document.getElementById("practice-section");
  const quizSection = document.getElementById("quiz-section");

  let currentMode = null;

  // Mode buttons
  document.getElementById("mode-practice").addEventListener("click", () => {
    currentMode = "practice";
    categoryButtons.classList.remove("hidden");
    practiceSection.classList.remove("hidden");
    quizSection.classList.add("hidden");
  });

  document.getElementById("mode-quiz").addEventListener("click", () => {
    currentMode = "quiz";
    categoryButtons.classList.remove("hidden");
    quizSection.classList.remove("hidden");
    practiceSection.classList.add("hidden");
  });

  // Category selection
  document.querySelectorAll(".category-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const type = btn.dataset.type;

      if (currentMode === "practice") {
        const questions = practiceQuestions[type];
        practiceDiv.innerHTML = questions
          .map((q, i) => `<p class="mb-3"><strong>Q${i + 1}:</strong> ${q}</p>`)
          .join("");
      } 
      else if (currentMode === "quiz") {
        loadQuiz(type);
      }
    });
  });
});
