document.addEventListener("DOMContentLoaded", () => {
  const inputs = document.querySelectorAll(".otp-input");
  const hiddenOtp = document.getElementById("otp-value");
  const form = document.getElementById("verify-form");

  if (!inputs.length || !hiddenOtp || !form) return;

  function updateOtp() {
    hiddenOtp.value = Array.from(inputs)
      .map(input => input.value)
      .join("");
    console.log("OTP BEFORE SUBMIT:", hiddenOtp.value);
  }

  // Handle submit
  form.addEventListener("submit", (e) => {
    updateOtp();

    if (hiddenOtp.value.length !== inputs.length) {
      e.preventDefault();
      alert("Please enter complete OTP");
      inputs[0].focus();
      return;
    }
  });

  // Handle typing + auto focus
  inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
      input.value = input.value.replace(/[^0-9]/g, "");

      if (input.value && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
      updateOtp();
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });

    // Handle paste (🔥 important)
    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const pasteData = e.clipboardData.getData("text").replace(/\D/g, "");
      pasteData.split("").forEach((char, i) => {
        if (inputs[i]) inputs[i].value = char;
      });
      updateOtp();
      inputs[Math.min(pasteData.length, inputs.length) - 1]?.focus();
    });
  });
});
