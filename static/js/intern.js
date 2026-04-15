function initVisitorForm() {
  var categorySelect = document.getElementById("visitor-category");
  var studentGroup = document.getElementById("student-number-group");
  if (!categorySelect || !studentGroup) return;

  function updateStudentField() {
    studentGroup.style.display =
      categorySelect.value === "UNISA student" ? "block" : "none";
  }

  categorySelect.addEventListener("change", updateStudentField);
  updateStudentField();
}

function initEditAssetModal() {
  var editAssetModal = document.getElementById("editAssetModal");
  if (!editAssetModal) return;

  editAssetModal.addEventListener("show.bs.modal", function (event) {
    var button = event.relatedTarget;
    var assetId = button.getAttribute("data-asset-id");
    document.getElementById("edit-asset-name").value =
      button.getAttribute("data-asset-name");
    document.getElementById("edit-asset-type").value =
      button.getAttribute("data-asset-type");
    document.getElementById("edit-asset-condition").value = button.getAttribute(
      "data-asset-condition",
    );
    document.getElementById("edit-asset-availability").value =
      button.getAttribute("data-asset-availability");
    document.getElementById("edit-asset-comments").value = button.getAttribute(
      "data-asset-comments",
    );
    document.getElementById("editAssetForm").action =
      "/intern/assets/" + assetId + "/edit";
  });
}

function initEditVisitorModal() {
  var editVisitorModal = document.getElementById("editVisitorModal");
  if (!editVisitorModal) return;

  var categorySelect = document.getElementById("edit-visitor-category");
  var studentGroup = document.getElementById("edit-student-number-group");

  function updateStudentField() {
    if (!categorySelect || !studentGroup) return;
    studentGroup.style.display =
      categorySelect.value === "UNISA student" ? "block" : "none";
  }

  if (categorySelect) {
    categorySelect.addEventListener("change", updateStudentField);
  }

  editVisitorModal.addEventListener("show.bs.modal", function (event) {
    var button = event.relatedTarget;
    var visitorId = button.getAttribute("data-visitor-id");
    document.getElementById("edit-visitor-name").value =
      button.getAttribute("data-visitor-name");
    document.getElementById("edit-visitor-category").value =
      button.getAttribute("data-visitor-category");
    document.getElementById("edit-student-number").value = button.getAttribute(
      "data-visitor-student-number",
    );
    document.getElementById("edit-visitor-email").value =
      button.getAttribute("data-visitor-email");
    document.getElementById("edit-visitor-phone").value =
      button.getAttribute("data-visitor-phone");
    document.getElementById("edit-visitor-reason").value = button.getAttribute(
      "data-visitor-reason",
    );
    document.getElementById("editVisitorForm").action =
      "/intern/visitors/" + visitorId + "/edit";
    updateStudentField();
  });
}

document.addEventListener("DOMContentLoaded", function () {
  initVisitorForm();
  initEditAssetModal();
  initEditVisitorModal();
});
