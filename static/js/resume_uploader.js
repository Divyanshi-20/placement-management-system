document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resume-form");
  const resultBox = document.getElementById("resume-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultBox.innerHTML = "<p class='text-gray-500'>Checking resume...</p>";
    resultBox.classList.remove("hidden");

    const formData = new FormData(form);

    try {
      const response = await fetch("/check_resume", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (data.error) {
        resultBox.innerHTML = `<p class="text-red-500 font-medium">${data.error}</p>`;
      } else {
        resultBox.innerHTML = `
          <h3 class="text-lg font-semibold mb-2">ATS Feedback:</h3>
          <div class="bg-gray-100 p-3 rounded text-sm whitespace-pre-wrap">${data.result}</div>
        `;
      }
    } catch (err) {
      resultBox.innerHTML = `<p class="text-red-500">Error: ${err.message}</p>`;
    }
  });
});
