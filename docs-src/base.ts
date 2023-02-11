import * as gadjet from 'gadjet/src/gadjet';
import { Adapter } from '@nitipit/adapter/dist/module/adapter';
import hljs from 'highlight.js/lib/core';
import shell from 'highlight.js/lib/languages/shell';
import python from 'highlight.js/lib/languages/python';
import * as colorDef from './_color';
import * as Color from 'color';
import { Icon } from '@nitipit/icon/src/icon';

import { Sidebar } from './_component/sidebar/sidebar';

let _scriptPath = document.currentScript!.src;
_scriptPath = new URL('./', _scriptPath);

Sidebar.define('el-sidebar');

hljs.registerLanguage('shell', shell);
hljs.registerLanguage('python', python);
hljs.highlightAll();

window.gadjet = gadjet;
window.colorDef = colorDef;
window.Adapter = Adapter;
window.Color = Color;

const bgColor = gadjet.bgColor;
const bgColorInt = gadjet.bgColorInt;
const Button = gadjet.Button;
const ButtonSquare = gadjet.ButtonSquare;
const ButtonPin = gadjet.ButtonPin;
const Tag = gadjet.Tag;
const Badge = gadjet.Badge;
const addStyle = gadjet.addStyle;
const fontFluid = gadjet.fontFluid;

let iconUrl = new URL('asset/icon/icomoon/symbol-defs.svg', _scriptPath);
Icon.href = iconUrl.toString();
customElements.define('el-icon', Icon);
gadjet.addStyle(`
    el-icon > svg {
        fill: currentColor;
    }
`)

Button.define('button');
ButtonSquare.define('el-button-square');
ButtonPin.define('el-button-pin');
Tag.define('el-tag');
Badge.define('el-badge');

ButtonSquare.tagStyle(`
    ${bgColorInt({color: colorDef.palette.red})}
`);

class CodeTitle extends Adapter {
    static initStyle(style) {
        super.initStyle(style);
        addStyle(`
            ${this.tagName} {
                ${bgColor(colorDef.palette.blue)}
                display: inline-block;
                padding: 0.1rem 0.3rem 0.1rem 0.3rem;
                border-radius: 5px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                border-bottom: 1px solid white;
            }
        `);
    };
};
CodeTitle.define('el-code-title');

const _scriptUrl = document.currentScript!.src;
const fontSansUrl = new URL('./asset/font/Fira_Sans/FiraSans-Regular.ttf', _scriptUrl);
const fontCodeUrl = new URL('./asset/font/Fira_Code/FiraCode-VariableFont_wght.ttf', _scriptUrl);

addStyle(`
@font-face {
    font-family: sans;
    src: url(${fontSansUrl});
}
@font-face {
    font-family: code;
    src: url(${fontCodeUrl});
}

html {
    font-family: sans;
    ${fontFluid({
        vwMin: 300,
        vwMax: 800,
        fontSizeMin: 14,
        fontSizeMax: 18
    })}
    line-height: 1.7;
}

body {
    margin: 0;
    padding-top: 2.5rem;
}

div.no-margin-next-element + * {
    margin-top: 0;
}

code {
    font-family: code;
    font-size: 0.9em;
    border-radius: 10px;
    ${bgColor(colorDef.palette.light)}
    padding: 0.1rem 0.5rem 0.1rem 0.5rem;
    line-height: 1.4;
}

pre {
    code {
        border-top-left-radius: 0;
    }
}

blockquote {
    display: block;
    padding: 0.1rem 1rem 0.2rem 1rem;
    margin-left: 1.5rem;
    border-left: 7px solid ${colorDef.theme['china-pink']};
    border-radius: 10px;
    border-top-left-radius: 0;
    ${bgColor(Color(colorDef.palette.light).lighten(0.1))}
}

.container {
    display: block;
    max-width: 1000px;
    width: 95%;
    min-width: 300px;
    margin: auto;
    &.text {
        h2 {
            margin-top: 3rem;
            & + hr {
                margin-top: -0.5rem;
                margin-bottom: 1.5rem;
            }
        }
    }
    @media only screen and (min-width: 1100px) {
        position: relative;
        left: 50px;
    }
}

.block {
    max-width: 400px;
    width: 100%;
}
`);