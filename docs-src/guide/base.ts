const addStyle = window.gadjet.addStyle;
const colorDef = window.colorDef;

addStyle`
h1 {
    text-align: center;
}

h2 {
    display: inline-block;
}

h2 + a {
    margin-left: 0.5rem;
    border: 2px solid ${colorDef.theme['ultra-red']};
    padding-left: 0.2rem;
    padding-right: 0.2rem;
    border-radius: 5px;
    &: hover {
        border: 3px solid ${colorDef.theme['ultra-red']};
    }
}
`