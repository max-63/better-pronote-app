const url_fetch_devoirs = document.getElementById('url_fetch_devoirs').getAttribute('data');
const div_devoirs = document.getElementById('devoirs-list');
const get_notes_url = document.getElementById('get_notes_url').getAttribute('data');
const div_notes = document.getElementById('note-list');

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
function isSameDay(d1, d2) {
    return d1.getFullYear() === d2.getFullYear() &&
           d1.getMonth() === d2.getMonth() &&
           d1.getDate() === d2.getDate();
}
function getWeekNumber(date) {
    // Calcule le numéro de la semaine ISO (lundi = début)
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7; // dimanche = 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

fetch(url_fetch_devoirs)
.then(response => response.json())
.then(data => {
    const devoirs = data.devoirs;
    const today = new Date();
    const currentWeek = getWeekNumber(today);
    const currentYear = today.getFullYear();

    // Filtrer pour garder que ceux de la semaine actuelle
    const devoirsSemaine = devoirs.filter(devoir => {
        const devoirDate = new Date(devoir.date_limite);
        return getWeekNumber(devoirDate) === currentWeek && devoirDate.getFullYear() === currentYear;
    });

    // Regrouper par date (comme avant)
    const devoirsParDate = {};
    devoirsSemaine.forEach(devoir => {
        const date = devoir.date_limite;
        if (!devoirsParDate[date]) {
            devoirsParDate[date] = [];
        }
        devoirsParDate[date].push(devoir);
    });

    const datesTriees = Object.keys(devoirsParDate).sort((a,b) => new Date(a) - new Date(b));

    let html = '<span class="travail-a-faire">Travail à faire cette semaine</span>';
    datesTriees.forEach(date => {
        const dateObj = new Date(date);
        let dateLisible = dateObj.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });
        html += `<div class="date-bloc"><h3 class="date-titre">📅 Pour ${dateLisible}</h3>`;
        devoirsParDate[date].forEach(devoir => {
            const matiere = devoir.titre;
            const couleur = matiereCouleurs[matiere] || '#bdc3c7';
            html += `
                <div class="devoir-item">
                    <div class="barre_couleur_matiere" style="--couleur: ${couleur};"></div>
                    <div class="texte_devoir">
                        <strong>${devoir.titre}</strong>
                        <label>${devoir.consigne}</label>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    });

    div_devoirs.innerHTML = html;

    // Reste de ton fetch notes (inchangé)
    fetch(get_notes_url)
    .then(response => response.json())
    .then(data => {
        const notes = data.notes;
        let html = '';
        let nb_notes = 0

        for (let note of notes) {
            note.date = new Date(note.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
            html += `
                <div class="note">
                    <div class="note_entete">
                        <span class="note_matiere">${note.matiere}</span>
                        <span class="note_encadree">
                            ${note.note}${note.sur != 20 ? ' / ' + note.sur : ''}
                        </span>
                    </div>
                    <p>${note.date}</p>
                </div>
            `;

            nb_notes ++;
            if (nb_notes === 10) {
                break
            }
        }
        div_notes.innerHTML = html;
    });
});




