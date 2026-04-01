document.addEventListener("DOMContentLoaded", () => {

  document.body.style.opacity = "0";
  document.body.style.transition = "opacity 0.35s ease";
  requestAnimationFrame(() => {
    document.body.style.opacity = "1";
  });

  const firstInput = document.querySelector("input, select, textarea");
  if (firstInput) firstInput.focus();

  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector("button[type='submit']");
      if (!btn) return;

      btn.dataset.text = btn.innerText;
      btn.innerText = "Please wait...";
      btn.disabled = true;
      btn.classList.add("loading");
    });
  });

  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-right a").forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });


  if ("ontouchstart" in window) {
    document.body.classList.add("touch-device");
  }

});

window.showToast = function (msg, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerText = msg;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 50);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
};

function enableEdit(id) {
  const input = document.getElementById(id);
  input.disabled = false;
  input.focus();

  const saveBtn = document.getElementById("saveBtn");
  if (saveBtn) {
    saveBtn.style.display = "block";
  }
}

function enableEdit(){

document.getElementById("username").removeAttribute("readonly");
document.getElementById("email").removeAttribute("readonly");

document.getElementById("saveBtn").style.display = "inline-block";
document.getElementById("editBtn").style.display = "none";

}