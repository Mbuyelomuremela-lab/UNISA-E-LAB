document.addEventListener("DOMContentLoaded", function () {
  var editUserModal = document.getElementById("editUserModal");
  if (editUserModal) {
    editUserModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var userId = button.getAttribute("data-user-id");
      var name = button.getAttribute("data-user-name");
      var email = button.getAttribute("data-user-email");
      var role = button.getAttribute("data-user-role");
      var status = button.getAttribute("data-user-status");
      var labId = button.getAttribute("data-user-lab");

      document.getElementById("edit-user-name").value = name;
      document.getElementById("edit-user-email").value = email;
      document.getElementById("edit-user-role").value = role;
      document.getElementById("edit-user-status").value = status;
      document.getElementById("edit-user-lab").value = labId;
      document.getElementById("editUserForm").action =
        "/admin/users/" + userId + "/edit";
    });
  }

  var resetPasswordModal = document.getElementById("resetPasswordModal");
  if (resetPasswordModal) {
    resetPasswordModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var userId = button.getAttribute("data-user-id");
      var name = button.getAttribute("data-user-name");
      document.getElementById("reset-user-name").textContent = name;
      document.getElementById("resetPasswordForm").action =
        "/admin/users/" + userId + "/reset";
    });
  }

  var editAssetModal = document.getElementById("editAssetModal");
  if (editAssetModal) {
    editAssetModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var assetId = button.getAttribute("data-asset-id");
      document.getElementById("edit-asset-name").value =
        button.getAttribute("data-asset-name");
      document.getElementById("edit-asset-serial-number").value =
        button.getAttribute("data-asset-serial-number");
      document.getElementById("edit-asset-unisa-number").value =
        button.getAttribute("data-asset-unisa-number");
      document.getElementById("edit-asset-type").value =
        button.getAttribute("data-asset-type");
      document.getElementById("edit-asset-condition").value =
        button.getAttribute("data-asset-condition");
      document.getElementById("edit-asset-availability").value =
        button.getAttribute("data-asset-availability");
      document.getElementById("edit-asset-comments").value =
        button.getAttribute("data-asset-comments");
      document.getElementById("edit-asset-lab").value =
        button.getAttribute("data-asset-lab");
      document.getElementById("editAssetForm").action =
        "/admin/assets/" + assetId + "/edit";
    });
  }

  var editLabModal = document.getElementById("editLabModal");
  if (editLabModal) {
    editLabModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var labId = button.getAttribute("data-lab-id");
      document.getElementById("edit-lab-name").value =
        button.getAttribute("data-lab-name");
      document.getElementById("edit-lab-province").value =
        button.getAttribute("data-lab-province");
      document.getElementById("edit-lab-latitude").value =
        button.getAttribute("data-lab-latitude");
      document.getElementById("edit-lab-longitude").value =
        button.getAttribute("data-lab-longitude");
      document.getElementById("edit-lab-address").value =
        button.getAttribute("data-lab-address");
      document.getElementById("edit-lab-description").value =
        button.getAttribute("data-lab-description");
      document.getElementById("editLabForm").action =
        "/admin/labs/" + labId + "/edit";
    });
  }

  var editProvinceModal = document.getElementById("editProvinceModal");
  if (editProvinceModal) {
    editProvinceModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var provinceId = button.getAttribute("data-province-id");
      document.getElementById("edit-province-name").value =
        button.getAttribute("data-province-name");
      document.getElementById("editProvinceForm").action =
        "/admin/provinces/" + provinceId + "/edit";
    });
  }

  function initSelectableTable(type) {
    var container = document.querySelector(
      ".selectable-" + type.toLowerCase() + "-table",
    );
    if (!container) return;

    var rows = container.querySelectorAll("tbody tr.selectable-row");
    var selectedRow = null;

    function updateButtons() {
      var editButton = document.getElementById("editSelected" + type);
      var deleteButton = document.getElementById("deleteSelected" + type);
      var resetButton = document.getElementById("resetSelected" + type);
      [editButton, deleteButton, resetButton].forEach(function (button) {
        if (button) button.disabled = !selectedRow;
      });
    }

    function selectRow(row) {
      if (selectedRow) {
        selectedRow.classList.remove("table-primary");
      }
      selectedRow = row;
      if (selectedRow) {
        selectedRow.classList.add("table-primary");
      }
      updateButtons();
    }

    rows.forEach(function (row) {
      row.addEventListener("click", function (event) {
        if (event.target.closest("button, a, input, form")) {
          return;
        }
        if (selectedRow === row) {
          selectRow(null);
        } else {
          selectRow(row);
        }
      });
    });

    var editButton = document.getElementById("editSelected" + type);
    if (editButton) {
      editButton.addEventListener("click", function () {
        if (!selectedRow) return;
        var modal = document.getElementById("edit" + type + "Modal");
        if (!modal) return;
        var bsModal = bootstrap.Modal.getOrCreateInstance(modal);
        var rowData = selectedRow.dataset;
        Object.keys(rowData).forEach(function (key) {
          var fieldName = key
            .replace(/([A-Z])/g, "-$1")
            .replace(/_/g, "-")
            .toLowerCase();
          var field = document.getElementById(
            "edit-" + type.toLowerCase() + "-" + fieldName,
          );
          if (field) {
            field.value = rowData[key];
          }
        });
        var form = modal.querySelector("form");
        if (form) {
          form.action =
            "/admin/" +
            type.toLowerCase() +
            "s/" +
            selectedRow.dataset.itemId +
            "/edit";
        }
        bsModal.show();
      });
    }

    var deleteButton = document.getElementById("deleteSelected" + type);
    if (deleteButton) {
      deleteButton.addEventListener("click", function () {
        if (!selectedRow) return;
        var action =
          "/admin/" +
          type.toLowerCase() +
          "s/" +
          selectedRow.dataset.itemId +
          "/delete";
        var hiddenForm = document.getElementById("selectedActionForm" + type);
        if (!hiddenForm) return;
        hiddenForm.action = action;
        var modalEl = document.getElementById("confirmActionModal");
        var confirmModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modalEl.querySelector(".confirm-action-message").textContent =
          "Delete the selected " + type.toLowerCase() + "?";
        var confirmBtn = modalEl.querySelector("#confirmActionBtn");
        confirmBtn.onclick = function () {
          confirmModal.hide();
          hiddenForm.submit();
        };
        confirmModal.show();
      });
    }

    var resetButton = document.getElementById("resetSelected" + type);
    if (resetButton) {
      resetButton.addEventListener("click", function () {
        if (!selectedRow) return;
        var modal = document.getElementById("resetPasswordModal");
        if (!modal) return;
        var selectedName =
          selectedRow.dataset.fullName || selectedRow.dataset.name || "";
        document.getElementById("reset-user-name").textContent = selectedName;
        var form = modal.querySelector("form");
        form.action = "/admin/users/" + selectedRow.dataset.itemId + "/reset";
        var bsModal = bootstrap.Modal.getOrCreateInstance(modal);
        bsModal.show();
      });
    }

    updateButtons();
  }

  initSelectableTable("User");
  initSelectableTable("Lab");
  initSelectableTable("Asset");
});
