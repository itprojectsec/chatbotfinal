document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("user-data-form");
  const messageContainer = document.getElementById("message-container");

  const displayMessage = (message, isError = false) => {
    messageContainer.textContent = message;
    messageContainer.style.color = isError ? "red" : "black";
  };

  const validateData = (data) => {
    // Verificar que la edad esté dentro del rango permitido
    if (data.age < 18 || data.age > 130) {
      displayMessage("La edad debe estar entre 18 y 130 años.", true);
      return false;
    }

    // Verificar que el número de cédula tenga la longitud correcta
    if (data.id_number.length !== 10) {
      displayMessage("El número de cédula es inválido.", true);
      return false;
    }

    // Verificar que el estado civil sea válido
    const validMaritalStatus = ["casado", "soltero", "viudo", "divorciado"];
    if (!validMaritalStatus.includes(data.marital_status.toLowerCase())) {
      displayMessage(
        "Por favor, ingresa una opción válida para el estado civil.",
        true
      );
      return false;
    }

    // Verificar que la adquisición de la propiedad sea válida
    const validPropertyAcquisition = ["compraventa", "donación", "herencia"];
    if (
      !validPropertyAcquisition.includes(
        data.property_acquisition.toLowerCase()
      )
    ) {
      displayMessage(
        "Por favor, ingresa una opción válida para la adquisición de la propiedad.",
        true
      );
      return false;
    }

    // Añade más validaciones según sea necesario

    // Si todos los datos son válidos, devuelve true
    return true;
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const userData = Object.fromEntries(formData.entries());

    if (!validateData(userData)) {
      return;
    }

    // Enviar datos al servidor para procesarlos
    fetch("/process_data", {
      method: "POST",
      body: JSON.stringify(userData),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // Mostrar resultados o mensajes en la página según sea necesario
        displayMessage(data.message);
      })
      .catch((error) => {
        console.error("Error:", error);
        displayMessage(
          "Error al procesar los datos. Por favor, inténtalo de nuevo.",
          true
        );
      });
  });
});
