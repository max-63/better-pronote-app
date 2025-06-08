const url_fetch_edt = document.getElementById('url_fetch_edt').getAttribute('data');

fetch(url_fetch_edt)
  .then(response => {
    if (!response.ok) throw new Error("Erreur lors du téléchargement");
    return response.arrayBuffer();
  })
  .then(data => {
    const loadingTask = pdfjsLib.getDocument({data});
    loadingTask.promise.then(pdf => {
      // Afficher la première page par exemple
      pdf.getPage(1).then(page => {
        const scale = 1.5;
        const viewport = page.getViewport({scale});
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
          canvasContext: context,
          viewport: viewport
        };
        page.render(renderContext).promise.then(() => {
          const pdfDiv = document.getElementById('edt');
          pdfDiv.innerHTML = ''; // vide
          pdfDiv.appendChild(canvas); // ajoute le canvas avec la page PDF rendue
        });
      });
    });
  })
  .catch(error => {
    console.error("Erreur fetch PDF:", error);
  });