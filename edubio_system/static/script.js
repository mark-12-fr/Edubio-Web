function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    if (icon) icon.classList.add("active");
  } else {
    input.type = "password";
    if (icon) icon.classList.remove("active");
  }
}


function searchStudent() {
  const input =
    document.getElementById("searchInput")?.value.toUpperCase() || "";
  const rows = document.getElementsByClassName("student-row");

  for (let i = 0; i < rows.length; i++) {
    const idText =
      rows[i].querySelector(".student-id")?.innerText.toUpperCase() || "";

    rows[i].style.display = idText.includes(input) ? "" : "none";
  }
}


function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  toast.innerHTML = `
    <span class="toast-icon">
      ${type === "error" ? "⚠" : "✔"}
    </span>
    <span class="toast-text">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 50);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}


if (typeof io !== "undefined") {
  const socket = io();

  socket.on("reload_page", function () {
    location.reload();
  });
}