import { Sidebar as _Sidebar,
    ButtonSquare,
    addStyle
} from 'gadjet/src/gadjet';

import { render, html } from 'uhtml';

import  * as colorDef  from '../../_color';
import { bgColorInt } from 'gadjet/src/style';

class SidebarButton extends ButtonSquare {
    static initStyle(): void {
        super.initStyle();
        this.tagStyle(`
            position: fixed;
            top: 0;
            left: 0;
            font-size: 1.5em;
            border-radius: 0;
            border-bottom-right-radius: 10px;
            ${bgColorInt({color: colorDef.palette.red})}
        `)
    }

    constructor() {
        super();
        this.render();
    }

    render() {
        render(this, html`
            <el-icon name="menu"></el-icon>
        `)
    }
}

export class Sidebar extends _Sidebar {
    static define(tagName: string): void {
        super.define(tagName);
        SidebarButton.define('el-sidebar-button');
    }

    static initStyle(): void {
        super.initStyle();
        addStyle(`
            a {
                text-decoration: none;
                color: inherit;
            }

            [el="title"] {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                color: ${colorDef.theme['ultra-red']};
                font-weight: bold;
                border-bottom: 2px solid;
                [el="home"] {
                    display: flex;
                    justify-content: center;
                    width: 100%;
                    font-size: 1.5em;
                    line-height: 2;
                }
                [el="close"] {
                    align-self: self-start;
                    el-button-square {
                        font-size: 1.5rem;
                        border-radius: 0;
                    }
                }
            }

            [el="menu"] {
                padding-top: 0.5rem;
                a {
                    display: block;
                    width: 100%;
                    line-height: 2;
                    font-size: 1.1em;
                    padding-left: 0.5rem;
                    &:hover {
                        ${bgColorInt({color: colorDef.theme['ultra-red']})}
                    }
                }
                ul {
                    margin: 0;
                    list-style: none;
                    padding-left: 1rem;
                }
            }
        `);
    }

    render() {
        super.render();
        const sidebarCloseButton = this.querySelector('[el="close"]');
        sidebarCloseButton?.addEventListener('click', () => {
            this.hide();
        });
        const sidebarButton = document.createElement('el-sidebar-button');
        document.body.append(sidebarButton);
        sidebarButton.addEventListener('click', () => {
            this.show();
        })
    }
};