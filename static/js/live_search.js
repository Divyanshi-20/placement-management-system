async function liveSearch() {
  const q = document.getElementById("search-query").value.trim();
  let res = await fetch(`/api/search_placements?q=${encodeURIComponent(q)}`);
  let data = await res.json();
  let div = document.getElementById("search-results");
  div.innerHTML = "";

  if (!data.results.length) {
    div.innerHTML = "<p>No jobs found.</p>";
    return;
  }

  data.results.forEach(job => {
    let el = document.createElement("div");
    el.className = "card p-2 mb-2";
    el.innerHTML = `
      <h5>${job.title}</h5>
      <p><b>${job.company}</b>${job.location ? " - " + job.location : ""}</p>
      <p>${job.description}</p>
    `;
    div.appendChild(el);
  });
}
