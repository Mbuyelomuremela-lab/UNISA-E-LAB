document.addEventListener("DOMContentLoaded", function () {
  var newPassword = document.getElementById("newPassword");
  var confirmPassword = document.getElementById("confirmPassword");
  var passwordStrength = document.getElementById("passwordStrength");
  var passwordMatch = document.getElementById("passwordMatch");
  var form = document.getElementById("changePasswordForm");

  function isStrongPassword(value) {
    var hasLower = /[a-z]/.test(value);
    var hasUpper = /[A-Z]/.test(value);
    var hasNumber = /[0-9]/.test(value);
    var hasSymbol = /[^A-Za-z0-9]/.test(value);
    return value.length >= 10 && hasLower && hasUpper && hasNumber && hasSymbol;
  }

  function updateFeedback() {
    if (!newPassword.value) {
      passwordStrength.textContent =
        "Must be 10+ characters and include uppercase, lowercase, digits, and symbols.";
      passwordStrength.className = "form-text text-muted";
    } else if (isStrongPassword(newPassword.value)) {
      passwordStrength.textContent = "Strong password format.";
      passwordStrength.className = "form-text text-success";
    } else {
      passwordStrength.textContent =
        "Password needs uppercase, lowercase, digits, symbols, and at least 10 characters.";
      passwordStrength.className = "form-text text-danger";
    }

    if (!confirmPassword.value) {
      passwordMatch.textContent = "";
    } else if (newPassword.value === confirmPassword.value) {
      passwordMatch.textContent = "Passwords match.";
      passwordMatch.className = "form-text text-success";
    } else {
      passwordMatch.textContent = "Passwords do not match.";
      passwordMatch.className = "form-text text-danger";
    }
  }

  newPassword.addEventListener("input", updateFeedback);
  confirmPassword.addEventListener("input", updateFeedback);

  form.addEventListener("submit", function (event) {
    if (
      !isStrongPassword(newPassword.value) ||
      newPassword.value !== confirmPassword.value
    ) {
      event.preventDefault();
      event.stopPropagation();
      updateFeedback();
      return;
    }
  });
});
