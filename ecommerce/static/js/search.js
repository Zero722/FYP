new Autocomplete("#autocomplete", {
    search: (input) => {
        console.log(input);
        const url = `get-products/?search=${input}`;
        return new Promise((resolve) => {
            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    console.log(data.payload);
                    resolve(data.payload);
                });
        });
    },
    renderResult: (result, props) => {
        console.log(props);

        let group = "";
        if (result.index % 3 == 0) {
            group = `<li class='group'>Groups</li>`;
        }
        return `
        ${group}

        <a href="product/${result.id}/">
        <li ${props}>
            <div class='wiki-title'>
                <img src="${result.imgurl}" height=30 width=30%>
                ${result.name}
                </div>
                </li>
            </a>

        `;
    },
    getResultValue: (result) => result.name,
});