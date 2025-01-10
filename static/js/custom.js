document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");
    const progressBar = document.getElementById("progress-bar");
    const dropArea = document.getElementById("drop-area");

    // Affiche le formulaire lors de l'interaction avec la dropzone
    dropArea.addEventListener("click", function () {
        uploadForm.classList.remove("d-none");
    });

    uploadForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);
        const xhr = new XMLHttpRequest();

        xhr.open("POST", uploadForm.action, true);

        xhr.upload.addEventListener("progress", function (event) {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                progressBar.style.width = percentComplete + "%";
                progressBar.setAttribute("aria-valuenow", percentComplete);
                progressBar.textContent = Math.round(percentComplete) + "%";
            }
        });

        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    progressBar.textContent = "Upload Complete!";
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    progressBar.textContent = "Error!";
                    alert(response.error || "An error occurred during upload.");
                }
            } else {
                progressBar.textContent = "Error!";
                alert("An unexpected error occurred.");
            }
        };

        xhr.send(formData);
    });

    dropArea.addEventListener("dragover", function (event) {
        event.preventDefault();
        dropArea.classList.add("bg-light");
    });

    dropArea.addEventListener("dragleave", function (event) {
        event.preventDefault();
        dropArea.classList.remove("bg-light");
    });

    dropArea.addEventListener("drop", function (event) {
        event.preventDefault();
        dropArea.classList.remove("bg-light");

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            const maxSize = 5 * 1024 * 1024; // 5MB size limit

            if (file.size > maxSize) {
                alert("File size exceeds the 5MB limit!");
                return;
            }

            if (![".csv", ".xls", ".xlsx"].includes(file.name.split('.').pop().toLowerCase())) {
                alert("Unsupported file format!");
                return;
            }

            const formData = new FormData();
            formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);
            formData.append("file", file);

            const xhr = new XMLHttpRequest();
            xhr.open("POST", uploadForm.action, true);

            xhr.upload.addEventListener("progress", function (event) {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    progressBar.style.width = percentComplete + "%";
                    progressBar.setAttribute("aria-valuenow", percentComplete);
                    progressBar.textContent = Math.round(percentComplete) + "%";
                }
            });

            xhr.onload = function () {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        progressBar.textContent = "Upload Complete!";
                        setTimeout(() => window.location.reload(), 1000);
                    } else {
                        progressBar.textContent = "Error!";
                        alert(response.error || "An error occurred during upload.");
                    }
                } else {
                    progressBar.textContent = "Error!";
                    alert("An unexpected error occurred.");
                }
            };

            xhr.send(formData);
        }
    });

    // Confirmation de suppression et suppression via AJAX
    const deleteButtons = document.querySelectorAll(".btn-danger");

    deleteButtons.forEach((button) => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            if (confirm("Êtes-vous sûr de vouloir supprimer ce fichier ?")) {
                fetch(button.href, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({}),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            alert(data.message);
                            window.location.reload();
                        } else {
                            alert("Une erreur s'est produite !");
                        }
                    })
                    .catch((error) => console.error("Erreur :", error));
            }
        });
    });

    // Fonction pour obtenir le cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Vérifiez si ce cookie commence par le nom recherché
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});