document.addEventListener('DOMContentLoaded', function () {
    const cardDetailModal = document.getElementById('cardDetailModal');
    if (cardDetailModal) {
        cardDetailModal.addEventListener('show.bs.modal', function (event) {
            // Button, der das Modal ausgelöst hat
            const triggerElement = event.relatedTarget;

            // URL aus dem data-Attribut extrahieren
            const cardUrl = triggerElement.getAttribute('data-card-url');

            const modalBody = cardDetailModal.querySelector('.modal-body');
            const modalTitle = cardDetailModal.querySelector('.modal-title');

            // Lade-Spinner anzeigen und Titel zurücksetzen
            modalTitle.textContent = 'Lade Kartendetails...';
            modalBody.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Laden...</span></div></div>';

            // Daten vom Server abrufen
            fetch(cardUrl)
                .then(response => response.text())
                .then(html => {
                    // Inhalt in das Modal einfügen
                    modalBody.innerHTML = html;
                    // Titel aus dem neuen Inhalt extrahieren und setzen
                    const newTitle = modalBody.querySelector('h2')?.textContent || 'Kartendetails';
                    modalTitle.textContent = newTitle;
                });
        });
    }

    // Verarbeite serverseitige Flash-Nachrichten beim Laden der Seite
    const flashMessages = document.querySelectorAll('#flash-messages-container .flash-message');
    flashMessages.forEach(flash => {
        const message = flash.dataset.message;
        const category = flash.dataset.category;
        showToast(message, category);
    });
});

document.addEventListener('submit', function(event) {
    // Prüfen, ob das Formular ein "collection-form" ist
    const form = event.target.closest('.collection-form');
    if (!form) {
        return;
    }

    // Standard-Formular-Absendung verhindern
    event.preventDefault();

    const url = form.action;
    const cardId = form.dataset.cardId;
    const buttonContainer = form.parentElement;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Signalisiert dem Server, dass es ein AJAX-Request ist
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Erstelle den neuen Button basierend auf der Antwort des Servers
            let newFormHtml;
            if (data.action_taken === 'added') {
                newFormHtml = `
                    <form action="/collection/remove/${cardId}" method="POST" class="d-inline collection-form" data-card-id="${cardId}" title="Aus Sammlung entfernen">
                        <button type="submit" class="btn btn-danger btn-sm" title="Aus Sammlung entfernen"><i class="bi bi-dash-lg"></i></button>
                    </form>
                `;
            } else {
                newFormHtml = `
                    <form action="/collection/add/${cardId}" method="POST" class="d-inline collection-form" data-card-id="${cardId}" title="Zur Sammlung hinzufügen">
                        <button type="submit" class="btn btn-success btn-sm" title="Zur Sammlung hinzufügen"><i class="bi bi-plus-lg"></i></button>
                    </form>
                `;
            }
            // Ersetze den alten Button-Container mit dem neuen
            buttonContainer.innerHTML = newFormHtml;

            // Zeige die Flash-Nachricht dynamisch an
            showToast(data.message, data.category);
        }
    });
});

/**
 * Zeigt eine "fliegende" Toast-Benachrichtigung an.
 * @param {string} message Die anzuzeigende Nachricht.
 * @param {string} category Die Kategorie (z.B. 'success', 'info', 'danger') für die Farbe.
 */
function showToast(message, category) {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    // Konvertiere Bootstrap-Kategorien in Hintergrundfarben
    const bgColor = category === 'danger' ? 'bg-danger' : (category === 'success' ? 'bg-success' : 'bg-primary');

    const toastHtml = `
        <div class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const newToastEl = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(newToastEl, { delay: 5000 }); // 5 Sekunden anzeigen
    toast.show();
}