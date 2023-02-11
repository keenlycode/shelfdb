addStyle = window.gadjet.addStyle;
fontFluid = window.gadjet.fontFluid;
bgColor = window.gadjet.bgColor;
bgColorInt = window.gadjet.bgColorInt;
colorDef = window.colorDef;
Adapter = window.Adapter;
Color = window.Color;

class Header extends Adapter {};
Header.define('el-header');

let color = Color(colorDef.theme['ultra-red']).darken(0.2);

Header.tagStyle(`
    display: flex;
    justify-content: center;
    align-items: center;
    color: ${color};
    div.container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        align-content: center;
        h1 {
            ${fontFluid({
                vwMin: 300,
                vwMax: 1200,
                fontSizeMin: 35,
                fontSizeMax: 80
            })}
            width: 100%;
            text-align: center;
            font-size: 4em;
            margin: 0.2em;
        }
        h2 {
            ${fontFluid({
                vwMin: 300,
                vwMax: 1200,
                fontSizeMin: 20,
                fontSizeMax: 40
            })}

            font-size: 2em;
            width: 100%;
            text-align: center;
            margin: 0.2em;
        }
        button[el="guide"] {
            ${bgColorInt({color: colorDef.palette.purple})}
        }
        button[el="github"] {
            ${bgColorInt({color: colorDef.palette.dark})}
        }
    }
`);