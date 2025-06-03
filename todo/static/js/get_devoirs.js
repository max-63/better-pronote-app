const url_fetch_devoirs = document.getElementById('url_fetch_devoirs').getAttribute('data');
const div_devoirs = document.getElementById('devoirs-list');
const get_notes_url = document.getElementById('get_notes_url').getAttribute('data');

const matiereCouleurs = {
    "MATHEMATIQUES": "#3498db",        // bleu
    "FRANCAIS": "#e67e22",     // orange
    "ANGLAIS": "#2ecc71",      // vert
    "ESPAGNOL": "#f39c12",     // jaune foncé
    "SCIENCES VIE & TERRE": "#27ae60",          // vert forêt
    "PHYSIQUE-CHIMIE": "#9b59b6", // violet
    "Technologie": "#1abc9c",  // turquoise
    "HISTOIRE-GEOGRAPHIE": "#e74c3c",     // rouge clair
    "HGGSP": "#8e44ad",        // violet foncé
    "NSI": "#34495e",          // bleu/gris foncé
    "EMC": "#95a5a6",          // gris clair
    "ALLEMAND": "#16a085",     // vert turquoise
    "LATIN": "#d35400",        // orange foncé
    "ARTS PLASTIQUES": "#ff69b4", // rose
    "EDUCATION MUSICALE": "#2980b9",      // bleu profond
    "ED.PHYSIQUE & SPORT.": "#2c3e50",          // gris/bleu foncé
};


fetch(url_fetch_devoirs)
.then(response => response.json())
.then(data => {
    const devoirs = data.devoirs;
    console.log(devoirs);

    // Regrouper les devoirs par date
    const devoirsParDate = {};

    devoirs.forEach(devoir => {
        const date = devoir.date_limite;
        if (!devoirsParDate[date]) {
            devoirsParDate[date] = [];
        }
        devoirsParDate[date].push(devoir);
    });

    // Trier les dates dans l'ordre chronologique
    const datesTriees = Object.keys(devoirsParDate).sort((a, b) => new Date(a) - new Date(b));

    // Générer le HTML
    let html = '';
    datesTriees.forEach(date => {
        html += `<div class="date-bloc"><h2>📅 Pour le ${date}</h2>`;
        devoirsParDate[date].forEach(devoir => {
            const matiere = devoir.titre;
            const couleur = matiereCouleurs[matiere] || '#bdc3c7'; // couleur par défaut si inconnue
            html += `
                <p>
                <span class="barre_couleur_matiere" style="--couleur: ${couleur};">|</span>
                <strong>${devoir.titre}</strong>: ${devoir.consigne}
                </p>
            `;


        });
        html += `</div>`;
    });

    div_devoirs.innerHTML = html;

    fetch(get_notes_url)
    .then(response => response.json())
    .then(data => {
        let moyenne = 0;
        let nb_notes = 0;
        const notes = data.notes;
        console.log(notes);
        let html = '';

        notes.forEach(note => {
            html += `
                <div class="note">
                    <h2>${note.matiere}</h2>
                    <p>Note: ${note.note} / ${note.sur}</p>
                    <p>${note.date}</p>
                </div>
            `;

            const n = parseFloat(note.note);  // conversion ici
            const c = parseFloat(note.coef);  // conversion ici

            if (!isNaN(n) && !isNaN(c)) {
                moyenne += n * c;
                nb_notes += c;
            } else {
                console.warn(`Note ou coef invalide: note="${note.note}", coef="${note.coef}"`);
            }
        });

        const moyenne_g = nb_notes > 0 ? (moyenne / nb_notes).toFixed(2) : "Aucune note valide";
        html += `<h1>Moyenne générale : ${moyenne_g}</h1>`;
        div_devoirs.innerHTML += html;
    });

});




