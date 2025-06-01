const url_fetch_devoirs = document.getElementById('url_fetch_devoirs').getAttribute('data');
const div_devoirs = document.getElementById('devoirs-list');


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