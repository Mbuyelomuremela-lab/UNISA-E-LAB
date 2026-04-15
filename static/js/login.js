function requestGeolocation(token) {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    function (position) {
      fetch("/validate_location", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: token,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }),
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (payload) {
          if (payload.success) {
            window.location.href = payload.redirect;
          } else {
            alert(payload.message || "Unable to validate location.");
          }
        })
        .catch(function () {
          alert("Network error while validating location.");
        });
    },
    function () {
      alert("Unable to retrieve location. Please allow location services.");
    },
    { enableHighAccuracy: true },
  );
}

function initQrVerify(token) {
  var button = document.getElementById("locate-button");
  if (button) {
    button.addEventListener("click", function () {
      requestGeolocation(token);
    });
  }
}
