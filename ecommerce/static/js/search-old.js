const search = document.getElementById('search');
const matchList = document.getElementById('match-list');

// Search search-data.json and filter it
const searchProducts = async searchText => {
    const res = await fetch('/static/search-data/search-data.json');
    const data = await res.json();

    // Get matches to current text input
    let matches = data.filter(product => {
        const regex = new RegExp(`^${searchText}`, 'gi');
        return product.name.match(regex);
    });

    if (searchText.length === 0) {
        matches = [];
        matchList.innerHTML = '';
    }

    outputHtml(matches);
}

// Show results in HTML
const outputHtml = matches => {
    if (matches.length > 0) {
        const html = matches.map(match => `
        <div class="card card-body mb-1">
            <h4>${match.name}<span class="text-primary">${match.price}</span></h4>
        </div>
        `
        ).join('');

        matchList.innerHTML = html;
    }
}

search.addEventListener('input', () => searchProducts(search.value));