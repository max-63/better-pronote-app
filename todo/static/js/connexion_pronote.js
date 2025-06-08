const url_fetch_pronote_lie = document.getElementById('url_fetch_pronote_lie').getAttribute('data');
const url_liee_pronote = document.getElementById('url_liee_pronote').getAttribute('data');
const image_pronote = document.getElementById('pronote').getAttribute('data');
const pronote_logo = document.getElementById('pronote_logo').getAttribute('data');

fetch(url_fetch_pronote_lie)
.then(response => response.json())
.then(data => {
    if (data.message === "non") {
        const btn_pronote = document.getElementById('btn_pronote');
        btn_pronote.style.display = "flex";
        btn_pronote.innerHTML = `<button id="lie_pronote"><img src="${pronote_logo}" alt=""> Synchroniser son compte <img src="${image_pronote}" alt="Pronote"></button>`;

        document.getElementById("lie_pronote").addEventListener("click", () => {
            const isMobile = navigator.userAgent.match(/Android|webOS|iPhone|iPad|iPod|BlackBerry|Windows Phone/i);
            
            Swal.fire({
                title: 'Veuillez vous connecter sur votre compte Pronote',
                html: `
                    <label>Pour connecter votre compte Pronote, veuillez générer un QR code depuis Pronote ${isMobile ? "sur un ordinateur" : "et faire une capture d'écran"}.</label>
                    <form id="form_pronote" enctype="multipart/form-data">
                        <label>${isMobile ? "Prenez une photo" : "Capture d'écran"} du QR code</label>
                        <input type="file" name="qrcode" accept="image/*" required>
                        <label>Entrez le code PIN du QR code</label>
                        <input type="text" name="code_pin" required>
                    </form>
                `,
                showCancelButton: false,
                showCloseButton: true,
                confirmButtonText: 'Valider',
                preConfirm: () => {
                    const form = Swal.getPopup().querySelector('#form_pronote');
                    const formData = new FormData(form);

                    return fetch(url_liee_pronote, {
                        method: 'POST',
                        body: formData,
                    })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(err => {
                                throw new Error(err.detail || response.statusText);
                            });
                        }
                        return response.json();
                    })
                    .catch(error => {
                        Swal.showValidationMessage(`Erreur: ${error.message}`);
                        return { message: 'error', detail: error.message };
                    });
                }
            }).then(result => {
                if (result.isConfirmed && result.value) {
                    if (result.value.message === "ok") {
                        Swal.fire('Succès!', result.value.detail, 'success').then(() => location.reload());
                    } else {
                        Swal.fire('Erreur', result.value.detail || 'Une erreur est survenue.', 'error');
                    }
                }
            });
        });
    } else {
        console.log("Compte déjà lié ✅");
        const btn_pronote = document.getElementById('btn_pronote');
        btn_pronote.style.display = "none";
    }
});
