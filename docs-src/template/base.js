import {render, html, repeat} from 'lit-html';

window.render = render;
window.html = html;

class Path extends HTMLElement {
    constructor() {
        super();
    }

    template(el_a_items) {
        return html`
        <ul class="bits-path bits-tag">
            ${el_a_items}
        </ul>
        `
    }

    connectedCallback() {
        let el_a_items = [];
        for (const el_a of this.querySelectorAll('a')) {
            el_a_items.push(html`<li>${el_a}</li>`);
        }
        render(this.template(el_a_items), this);
    }
}

customElements.define('el-path', Path);