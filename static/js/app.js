document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("button, a.btn").forEach(function (item) {
    item.addEventListener("click", function () {
      var audio = document.getElementById("click-sound");
      if (audio) audio.play();
    });
  });

  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        return;
      }

      var btn = form.querySelector("[data-loading]");
      if (!btn) {
        return;
      }

      btn.disabled = true;
      btn.innerHTML =
        '<span class="spinner-border spinner-border-sm"></span> Loading...';
    });
  });

  var confirmButtons = document.querySelectorAll(".confirm-delete");
  confirmButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      event.preventDefault();
      var form = button.closest("form");
      if (!form) {
        return;
      }
      var message =
        button.getAttribute("data-confirm-message") ||
        "Are you sure you want to delete this item?";
      var modalEl = document.getElementById("confirmActionModal");
      var confirmModal = bootstrap.Modal.getOrCreateInstance(modalEl);
      modalEl.querySelector(".confirm-action-message").textContent = message;
      var confirmBtn = modalEl.querySelector("#confirmActionBtn");
      confirmBtn.onclick = function () {
        confirmModal.hide();
        form.submit();
      };
      confirmModal.show();
    });
  });
});
