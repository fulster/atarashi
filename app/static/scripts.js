function handleKeyPress(event) {
    if (event.key === "Enter") {
        const input = document.getElementById('ideaInput');
        const idea = input.value.trim();
        if (idea) {
            fetchKeywords(idea).then(keywords => {
                const list = document.getElementById('ideasList');
                const listItem = document.createElement('li');
                listItem.classList.add('list-group-item', 'idea-item');
                
                const ideaText = document.createElement('div');
                ideaText.textContent = idea;
                listItem.appendChild(ideaText);
                
                const keywordsContainer = document.createElement('div');
                keywordsContainer.classList.add('keywords');
                keywords.forEach(keyword => {
                    const badge = document.createElement('span');
                    badge.classList.add('badge', 'keyword-badge'); // Utilisez la nouvelle classe ici
                    badge.textContent = keyword;
                    keywordsContainer.appendChild(badge);
                });
                
                listItem.appendChild(keywordsContainer);
                list.appendChild(listItem);
                
                input.value = ''; // Clear input after adding
            });
        }
        input.focus(); // Refocus to input
    }
}

function fetchKeywords(text) {
    return fetch('/keywords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    })
    .then(response => response.json())
    .then(data => data.keywords);
}

function deleteIdea(ideaId) {
    fetch('/delete-idea/' + ideaId, {
        method: 'DELETE'
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Something went wrong');
    }).then(data => {
        console.log('Deleted:', data);
        window.location.reload();  // Recharge la page pour mettre à jour la liste
    }).catch(error => console.error('Error deleting the idea:', error));
}
