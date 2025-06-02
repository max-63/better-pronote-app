const url_fetch_devoirs = document.getElementById('url_fetch_devoirs').getAttribute('data');
const div_devoirs = document.getElementById('devoirs-list');
const get_notes_url = document.getElementById('get_notes_url').getAttribute('data');


fetch(url_fetch_devoirs)
.then(response => response.json())
.then(data => {
    const devoirs = data.devoirs;
    console.log(devoirs);
    let html = '';
    devoirs.forEach(devoir => {
        html += `
            <div class="devoir">
                <h2>${devoir.titre}</h2><p>A faire pour le ${devoir.date_limite}</p>
                <p>${devoir.consigne}</p>
            </div>
        `;
    });
    div_devoirs.innerHTML = html;
})

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
