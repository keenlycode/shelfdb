// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles

(function (modules, entry, mainEntry, parcelRequireName, globalName) {
  /* eslint-disable no-undef */
  var globalObject =
    typeof globalThis !== 'undefined'
      ? globalThis
      : typeof self !== 'undefined'
      ? self
      : typeof window !== 'undefined'
      ? window
      : typeof global !== 'undefined'
      ? global
      : {};
  /* eslint-enable no-undef */

  // Save the require from previous bundle to this closure if any
  var previousRequire =
    typeof globalObject[parcelRequireName] === 'function' &&
    globalObject[parcelRequireName];

  var cache = previousRequire.cache || {};
  // Do not use `require` to prevent Webpack from trying to bundle this call
  var nodeRequire =
    typeof module !== 'undefined' &&
    typeof module.require === 'function' &&
    module.require.bind(module);

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire =
          typeof globalObject[parcelRequireName] === 'function' &&
          globalObject[parcelRequireName];
        if (!jumped && currentRequire) {
          return currentRequire(name, true);
        }

        // If there are other bundles on this page the require from the
        // previous one is saved to 'previousRequire'. Repeat this as
        // many times as there are bundles until the module is found or
        // we exhaust the require chain.
        if (previousRequire) {
          return previousRequire(name, true);
        }

        // Try the node require function if it exists.
        if (nodeRequire && typeof name === 'string') {
          return nodeRequire(name);
        }

        var err = new Error("Cannot find module '" + name + "'");
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;
      localRequire.cache = {};

      var module = (cache[name] = new newRequire.Module(name));

      modules[name][0].call(
        module.exports,
        localRequire,
        module,
        module.exports,
        this
      );
    }

    return cache[name].exports;

    function localRequire(x) {
      var res = localRequire.resolve(x);
      return res === false ? {} : newRequire(res);
    }

    function resolve(x) {
      var id = modules[name][1][x];
      return id != null ? id : x;
    }
  }

  function Module(moduleName) {
    this.id = moduleName;
    this.bundle = newRequire;
    this.exports = {};
  }

  newRequire.isParcelRequire = true;
  newRequire.Module = Module;
  newRequire.modules = modules;
  newRequire.cache = cache;
  newRequire.parent = previousRequire;
  newRequire.register = function (id, exports) {
    modules[id] = [
      function (require, module) {
        module.exports = exports;
      },
      {},
    ];
  };

  Object.defineProperty(newRequire, 'root', {
    get: function () {
      return globalObject[parcelRequireName];
    },
  });

  globalObject[parcelRequireName] = newRequire;

  for (var i = 0; i < entry.length; i++) {
    newRequire(entry[i]);
  }

  if (mainEntry) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(mainEntry);

    // CommonJS
    if (typeof exports === 'object' && typeof module !== 'undefined') {
      module.exports = mainExports;

      // RequireJS
    } else if (typeof define === 'function' && define.amd) {
      define(function () {
        return mainExports;
      });

      // <script>
    } else if (globalName) {
      this[globalName] = mainExports;
    }
  }
})({"ek91E":[function(require,module,exports) {
var global = arguments[3];
var HMR_HOST = null;
var HMR_PORT = 1234;
var HMR_SECURE = false;
var HMR_ENV_HASH = "d6ea1d42532a7575";
module.bundle.HMR_BUNDLE_ID = "1fa1316db1b5154b";
"use strict";
/* global HMR_HOST, HMR_PORT, HMR_ENV_HASH, HMR_SECURE, chrome, browser, __parcel__import__, __parcel__importScripts__, ServiceWorkerGlobalScope */ /*::
import type {
  HMRAsset,
  HMRMessage,
} from '@parcel/reporter-dev-server/src/HMRServer.js';
interface ParcelRequire {
  (string): mixed;
  cache: {|[string]: ParcelModule|};
  hotData: {|[string]: mixed|};
  Module: any;
  parent: ?ParcelRequire;
  isParcelRequire: true;
  modules: {|[string]: [Function, {|[string]: string|}]|};
  HMR_BUNDLE_ID: string;
  root: ParcelRequire;
}
interface ParcelModule {
  hot: {|
    data: mixed,
    accept(cb: (Function) => void): void,
    dispose(cb: (mixed) => void): void,
    // accept(deps: Array<string> | string, cb: (Function) => void): void,
    // decline(): void,
    _acceptCallbacks: Array<(Function) => void>,
    _disposeCallbacks: Array<(mixed) => void>,
  |};
}
interface ExtensionContext {
  runtime: {|
    reload(): void,
    getURL(url: string): string;
    getManifest(): {manifest_version: number, ...};
  |};
}
declare var module: {bundle: ParcelRequire, ...};
declare var HMR_HOST: string;
declare var HMR_PORT: string;
declare var HMR_ENV_HASH: string;
declare var HMR_SECURE: boolean;
declare var chrome: ExtensionContext;
declare var browser: ExtensionContext;
declare var __parcel__import__: (string) => Promise<void>;
declare var __parcel__importScripts__: (string) => Promise<void>;
declare var globalThis: typeof self;
declare var ServiceWorkerGlobalScope: Object;
*/ var OVERLAY_ID = "__parcel__error__overlay__";
var OldModule = module.bundle.Module;
function Module(moduleName) {
    OldModule.call(this, moduleName);
    this.hot = {
        data: module.bundle.hotData[moduleName],
        _acceptCallbacks: [],
        _disposeCallbacks: [],
        accept: function(fn) {
            this._acceptCallbacks.push(fn || function() {});
        },
        dispose: function(fn) {
            this._disposeCallbacks.push(fn);
        }
    };
    module.bundle.hotData[moduleName] = undefined;
}
module.bundle.Module = Module;
module.bundle.hotData = {};
var checkedAssets /*: {|[string]: boolean|} */ , assetsToDispose /*: Array<[ParcelRequire, string]> */ , assetsToAccept /*: Array<[ParcelRequire, string]> */ ;
function getHostname() {
    return HMR_HOST || (location.protocol.indexOf("http") === 0 ? location.hostname : "localhost");
}
function getPort() {
    return HMR_PORT || location.port;
}
// eslint-disable-next-line no-redeclare
var parent = module.bundle.parent;
if ((!parent || !parent.isParcelRequire) && typeof WebSocket !== "undefined") {
    var hostname = getHostname();
    var port = getPort();
    var protocol = HMR_SECURE || location.protocol == "https:" && !/localhost|127.0.0.1|0.0.0.0/.test(hostname) ? "wss" : "ws";
    var ws = new WebSocket(protocol + "://" + hostname + (port ? ":" + port : "") + "/");
    // Web extension context
    var extCtx = typeof chrome === "undefined" ? typeof browser === "undefined" ? null : browser : chrome;
    // Safari doesn't support sourceURL in error stacks.
    // eval may also be disabled via CSP, so do a quick check.
    var supportsSourceURL = false;
    try {
        (0, eval)('throw new Error("test"); //# sourceURL=test.js');
    } catch (err) {
        supportsSourceURL = err.stack.includes("test.js");
    }
    // $FlowFixMe
    ws.onmessage = async function(event /*: {data: string, ...} */ ) {
        checkedAssets = {} /*: {|[string]: boolean|} */ ;
        assetsToAccept = [];
        assetsToDispose = [];
        var data /*: HMRMessage */  = JSON.parse(event.data);
        if (data.type === "update") {
            // Remove error overlay if there is one
            if (typeof document !== "undefined") removeErrorOverlay();
            let assets = data.assets.filter((asset)=>asset.envHash === HMR_ENV_HASH);
            // Handle HMR Update
            let handled = assets.every((asset)=>{
                return asset.type === "css" || asset.type === "js" && hmrAcceptCheck(module.bundle.root, asset.id, asset.depsByBundle);
            });
            if (handled) {
                console.clear();
                // Dispatch custom event so other runtimes (e.g React Refresh) are aware.
                if (typeof window !== "undefined" && typeof CustomEvent !== "undefined") window.dispatchEvent(new CustomEvent("parcelhmraccept"));
                await hmrApplyUpdates(assets);
                // Dispose all old assets.
                let processedAssets = {} /*: {|[string]: boolean|} */ ;
                for(let i = 0; i < assetsToDispose.length; i++){
                    let id = assetsToDispose[i][1];
                    if (!processedAssets[id]) {
                        hmrDispose(assetsToDispose[i][0], id);
                        processedAssets[id] = true;
                    }
                }
                // Run accept callbacks. This will also re-execute other disposed assets in topological order.
                processedAssets = {};
                for(let i = 0; i < assetsToAccept.length; i++){
                    let id = assetsToAccept[i][1];
                    if (!processedAssets[id]) {
                        hmrAccept(assetsToAccept[i][0], id);
                        processedAssets[id] = true;
                    }
                }
            } else fullReload();
        }
        if (data.type === "error") {
            // Log parcel errors to console
            for (let ansiDiagnostic of data.diagnostics.ansi){
                let stack = ansiDiagnostic.codeframe ? ansiDiagnostic.codeframe : ansiDiagnostic.stack;
                console.error("\uD83D\uDEA8 [parcel]: " + ansiDiagnostic.message + "\n" + stack + "\n\n" + ansiDiagnostic.hints.join("\n"));
            }
            if (typeof document !== "undefined") {
                // Render the fancy html overlay
                removeErrorOverlay();
                var overlay = createErrorOverlay(data.diagnostics.html);
                // $FlowFixMe
                document.body.appendChild(overlay);
            }
        }
    };
    ws.onerror = function(e) {
        console.error(e.message);
    };
    ws.onclose = function() {
        console.warn("[parcel] \uD83D\uDEA8 Connection to the HMR server was lost");
    };
}
function removeErrorOverlay() {
    var overlay = document.getElementById(OVERLAY_ID);
    if (overlay) {
        overlay.remove();
        console.log("[parcel] ✨ Error resolved");
    }
}
function createErrorOverlay(diagnostics) {
    var overlay = document.createElement("div");
    overlay.id = OVERLAY_ID;
    let errorHTML = '<div style="background: black; opacity: 0.85; font-size: 16px; color: white; position: fixed; height: 100%; width: 100%; top: 0px; left: 0px; padding: 30px; font-family: Menlo, Consolas, monospace; z-index: 9999;">';
    for (let diagnostic of diagnostics){
        let stack = diagnostic.frames.length ? diagnostic.frames.reduce((p, frame)=>{
            return `${p}
<a href="/__parcel_launch_editor?file=${encodeURIComponent(frame.location)}" style="text-decoration: underline; color: #888" onclick="fetch(this.href); return false">${frame.location}</a>
${frame.code}`;
        }, "") : diagnostic.stack;
        errorHTML += `
      <div>
        <div style="font-size: 18px; font-weight: bold; margin-top: 20px;">
          🚨 ${diagnostic.message}
        </div>
        <pre>${stack}</pre>
        <div>
          ${diagnostic.hints.map((hint)=>"<div>\uD83D\uDCA1 " + hint + "</div>").join("")}
        </div>
        ${diagnostic.documentation ? `<div>📝 <a style="color: violet" href="${diagnostic.documentation}" target="_blank">Learn more</a></div>` : ""}
      </div>
    `;
    }
    errorHTML += "</div>";
    overlay.innerHTML = errorHTML;
    return overlay;
}
function fullReload() {
    if ("reload" in location) location.reload();
    else if (extCtx && extCtx.runtime && extCtx.runtime.reload) extCtx.runtime.reload();
}
function getParents(bundle, id) /*: Array<[ParcelRequire, string]> */ {
    var modules = bundle.modules;
    if (!modules) return [];
    var parents = [];
    var k, d, dep;
    for(k in modules)for(d in modules[k][1]){
        dep = modules[k][1][d];
        if (dep === id || Array.isArray(dep) && dep[dep.length - 1] === id) parents.push([
            bundle,
            k
        ]);
    }
    if (bundle.parent) parents = parents.concat(getParents(bundle.parent, id));
    return parents;
}
function updateLink(link) {
    var href = link.getAttribute("href");
    if (!href) return;
    var newLink = link.cloneNode();
    newLink.onload = function() {
        if (link.parentNode !== null) // $FlowFixMe
        link.parentNode.removeChild(link);
    };
    newLink.setAttribute("href", // $FlowFixMe
    href.split("?")[0] + "?" + Date.now());
    // $FlowFixMe
    link.parentNode.insertBefore(newLink, link.nextSibling);
}
var cssTimeout = null;
function reloadCSS() {
    if (cssTimeout) return;
    cssTimeout = setTimeout(function() {
        var links = document.querySelectorAll('link[rel="stylesheet"]');
        for(var i = 0; i < links.length; i++){
            // $FlowFixMe[incompatible-type]
            var href /*: string */  = links[i].getAttribute("href");
            var hostname = getHostname();
            var servedFromHMRServer = hostname === "localhost" ? new RegExp("^(https?:\\/\\/(0.0.0.0|127.0.0.1)|localhost):" + getPort()).test(href) : href.indexOf(hostname + ":" + getPort());
            var absolute = /^https?:\/\//i.test(href) && href.indexOf(location.origin) !== 0 && !servedFromHMRServer;
            if (!absolute) updateLink(links[i]);
        }
        cssTimeout = null;
    }, 50);
}
function hmrDownload(asset) {
    if (asset.type === "js") {
        if (typeof document !== "undefined") {
            let script = document.createElement("script");
            script.src = asset.url + "?t=" + Date.now();
            if (asset.outputFormat === "esmodule") script.type = "module";
            return new Promise((resolve, reject)=>{
                var _document$head;
                script.onload = ()=>resolve(script);
                script.onerror = reject;
                (_document$head = document.head) === null || _document$head === void 0 || _document$head.appendChild(script);
            });
        } else if (typeof importScripts === "function") {
            // Worker scripts
            if (asset.outputFormat === "esmodule") return import(asset.url + "?t=" + Date.now());
            else return new Promise((resolve, reject)=>{
                try {
                    importScripts(asset.url + "?t=" + Date.now());
                    resolve();
                } catch (err) {
                    reject(err);
                }
            });
        }
    }
}
async function hmrApplyUpdates(assets) {
    global.parcelHotUpdate = Object.create(null);
    let scriptsToRemove;
    try {
        // If sourceURL comments aren't supported in eval, we need to load
        // the update from the dev server over HTTP so that stack traces
        // are correct in errors/logs. This is much slower than eval, so
        // we only do it if needed (currently just Safari).
        // https://bugs.webkit.org/show_bug.cgi?id=137297
        // This path is also taken if a CSP disallows eval.
        if (!supportsSourceURL) {
            let promises = assets.map((asset)=>{
                var _hmrDownload;
                return (_hmrDownload = hmrDownload(asset)) === null || _hmrDownload === void 0 ? void 0 : _hmrDownload.catch((err)=>{
                    // Web extension bugfix for Chromium
                    // https://bugs.chromium.org/p/chromium/issues/detail?id=1255412#c12
                    if (extCtx && extCtx.runtime && extCtx.runtime.getManifest().manifest_version == 3) {
                        if (typeof ServiceWorkerGlobalScope != "undefined" && global instanceof ServiceWorkerGlobalScope) {
                            extCtx.runtime.reload();
                            return;
                        }
                        asset.url = extCtx.runtime.getURL("/__parcel_hmr_proxy__?url=" + encodeURIComponent(asset.url + "?t=" + Date.now()));
                        return hmrDownload(asset);
                    }
                    throw err;
                });
            });
            scriptsToRemove = await Promise.all(promises);
        }
        assets.forEach(function(asset) {
            hmrApply(module.bundle.root, asset);
        });
    } finally{
        delete global.parcelHotUpdate;
        if (scriptsToRemove) scriptsToRemove.forEach((script)=>{
            if (script) {
                var _document$head2;
                (_document$head2 = document.head) === null || _document$head2 === void 0 || _document$head2.removeChild(script);
            }
        });
    }
}
function hmrApply(bundle /*: ParcelRequire */ , asset /*:  HMRAsset */ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (asset.type === "css") reloadCSS();
    else if (asset.type === "js") {
        let deps = asset.depsByBundle[bundle.HMR_BUNDLE_ID];
        if (deps) {
            if (modules[asset.id]) {
                // Remove dependencies that are removed and will become orphaned.
                // This is necessary so that if the asset is added back again, the cache is gone, and we prevent a full page reload.
                let oldDeps = modules[asset.id][1];
                for(let dep in oldDeps)if (!deps[dep] || deps[dep] !== oldDeps[dep]) {
                    let id = oldDeps[dep];
                    let parents = getParents(module.bundle.root, id);
                    if (parents.length === 1) hmrDelete(module.bundle.root, id);
                }
            }
            if (supportsSourceURL) // Global eval. We would use `new Function` here but browser
            // support for source maps is better with eval.
            (0, eval)(asset.output);
            // $FlowFixMe
            let fn = global.parcelHotUpdate[asset.id];
            modules[asset.id] = [
                fn,
                deps
            ];
        } else if (bundle.parent) hmrApply(bundle.parent, asset);
    }
}
function hmrDelete(bundle, id) {
    let modules = bundle.modules;
    if (!modules) return;
    if (modules[id]) {
        // Collect dependencies that will become orphaned when this module is deleted.
        let deps = modules[id][1];
        let orphans = [];
        for(let dep in deps){
            let parents = getParents(module.bundle.root, deps[dep]);
            if (parents.length === 1) orphans.push(deps[dep]);
        }
        // Delete the module. This must be done before deleting dependencies in case of circular dependencies.
        delete modules[id];
        delete bundle.cache[id];
        // Now delete the orphans.
        orphans.forEach((id)=>{
            hmrDelete(module.bundle.root, id);
        });
    } else if (bundle.parent) hmrDelete(bundle.parent, id);
}
function hmrAcceptCheck(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    if (hmrAcceptCheckOne(bundle, id, depsByBundle)) return true;
    // Traverse parents breadth first. All possible ancestries must accept the HMR update, or we'll reload.
    let parents = getParents(module.bundle.root, id);
    let accepted = false;
    while(parents.length > 0){
        let v = parents.shift();
        let a = hmrAcceptCheckOne(v[0], v[1], null);
        if (a) // If this parent accepts, stop traversing upward, but still consider siblings.
        accepted = true;
        else {
            // Otherwise, queue the parents in the next level upward.
            let p = getParents(module.bundle.root, v[1]);
            if (p.length === 0) {
                // If there are no parents, then we've reached an entry without accepting. Reload.
                accepted = false;
                break;
            }
            parents.push(...p);
        }
    }
    return accepted;
}
function hmrAcceptCheckOne(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (depsByBundle && !depsByBundle[bundle.HMR_BUNDLE_ID]) {
        // If we reached the root bundle without finding where the asset should go,
        // there's nothing to do. Mark as "accepted" so we don't reload the page.
        if (!bundle.parent) return true;
        return hmrAcceptCheck(bundle.parent, id, depsByBundle);
    }
    if (checkedAssets[id]) return true;
    checkedAssets[id] = true;
    var cached = bundle.cache[id];
    assetsToDispose.push([
        bundle,
        id
    ]);
    if (!cached || cached.hot && cached.hot._acceptCallbacks.length) {
        assetsToAccept.push([
            bundle,
            id
        ]);
        return true;
    }
}
function hmrDispose(bundle /*: ParcelRequire */ , id /*: string */ ) {
    var cached = bundle.cache[id];
    bundle.hotData[id] = {};
    if (cached && cached.hot) cached.hot.data = bundle.hotData[id];
    if (cached && cached.hot && cached.hot._disposeCallbacks.length) cached.hot._disposeCallbacks.forEach(function(cb) {
        cb(bundle.hotData[id]);
    });
    delete bundle.cache[id];
}
function hmrAccept(bundle /*: ParcelRequire */ , id /*: string */ ) {
    // Execute the module.
    bundle(id);
    // Run the accept callbacks in the new version of the module.
    var cached = bundle.cache[id];
    if (cached && cached.hot && cached.hot._acceptCallbacks.length) cached.hot._acceptCallbacks.forEach(function(cb) {
        var assetsToAlsoAccept = cb(function() {
            return getParents(module.bundle.root, id);
        });
        if (assetsToAlsoAccept && assetsToAccept.length) {
            assetsToAlsoAccept.forEach(function(a) {
                hmrDispose(a[0], a[1]);
            });
            // $FlowFixMe[method-unbinding]
            assetsToAccept.push.apply(assetsToAccept, assetsToAlsoAccept);
        }
    });
}

},{}],"3UFPP":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Sidebar", ()=>Sidebar);
var _gadjet = require("gadjet/src/gadjet");
var _uhtml = require("uhtml");
var _color = require("../../_color");
var _style = require("gadjet/src/style");
class SidebarButton extends (0, _gadjet.ButtonSquare) {
    static initStyle() {
        super.initStyle();
        this.tagStyle(`
            position: fixed;
            top: 0;
            left: 0;
            font-size: 1.5em;
            border-radius: 0;
            border-bottom-right-radius: 10px;
            ${(0, _style.bgColorInt)({
            color: _color.palette.red
        })}
        `);
    }
    constructor(){
        super();
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            <el-icon name="menu"></el-icon>
        `);
    }
}
class Sidebar extends (0, _gadjet.Sidebar) {
    static define(tagName) {
        super.define(tagName);
        SidebarButton.define("el-sidebar-button");
    }
    static initStyle() {
        super.initStyle();
        (0, _gadjet.addStyle)(`
            a {
                text-decoration: none;
                color: inherit;
            }

            [el="title"] {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                color: ${_color.theme["ultra-red"]};
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
                        ${(0, _style.bgColorInt)({
            color: _color.theme["ultra-red"]
        })}
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
        sidebarCloseButton?.addEventListener("click", ()=>{
            this.hide();
        });
        const sidebarButton = document.createElement("el-sidebar-button");
        document.body.append(sidebarButton);
        sidebarButton.addEventListener("click", ()=>{
            this.show();
        });
    }
}

},{"gadjet/src/gadjet":"2SrWz","uhtml":"if09d","../../_color":"lFBda","gadjet/src/style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2SrWz":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "define", ()=>(0, _adapter.define));
parcelHelpers.export(exports, "Badge", ()=>(0, _badge.Badge));
parcelHelpers.export(exports, "BoxArrow", ()=>(0, _boxArrow.BoxArrow));
parcelHelpers.export(exports, "Button", ()=>(0, _button.Button));
parcelHelpers.export(exports, "ButtonGroup", ()=>(0, _buttonGroup.ButtonGroup));
parcelHelpers.export(exports, "ButtonPin", ()=>(0, _buttonPin.ButtonPin));
parcelHelpers.export(exports, "ButtonSquare", ()=>(0, _buttonSquare.ButtonSquare));
parcelHelpers.export(exports, "Card", ()=>(0, _card.Card));
parcelHelpers.export(exports, "Checkbox", ()=>(0, _checkbox.Checkbox));
parcelHelpers.export(exports, "Input", ()=>(0, _input.Input));
parcelHelpers.export(exports, "InputDate", ()=>(0, _inputDate.InputDate));
parcelHelpers.export(exports, "InputNumber", ()=>(0, _inputNumber.InputNumber));
parcelHelpers.export(exports, "InputNumberCenter", ()=>(0, _inputNumberCenter.InputNumberCenter));
parcelHelpers.export(exports, "InputRadio", ()=>(0, _inputRadio.InputRadio));
parcelHelpers.export(exports, "InputTag", ()=>(0, _inputTag.InputTag));
parcelHelpers.export(exports, "Menu", ()=>(0, _menu.Menu));
parcelHelpers.export(exports, "ProgressBar", ()=>(0, _progressBar.ProgressBar));
parcelHelpers.export(exports, "ProgressCircle", ()=>(0, _progressCircle.ProgressCircle));
parcelHelpers.export(exports, "Sidebar", ()=>(0, _sidebar.Sidebar));
parcelHelpers.export(exports, "Switch", ()=>(0, _switch.Switch));
parcelHelpers.export(exports, "Tab", ()=>(0, _tab.Tab));
parcelHelpers.export(exports, "Table", ()=>(0, _table.Table));
parcelHelpers.export(exports, "Tag", ()=>(0, _tag.Tag));
parcelHelpers.export(exports, "TagX", ()=>(0, _tagx.TagX)) // export { FileManager } from './ui/file-manager/file-manager';
 // export { HTMLEditor } from './ui/html-editor/html-editor';
;
var _style = require("./style");
parcelHelpers.exportAll(_style, exports);
var _adapter = require("@nitipit/adapter/src/adapter");
var _badge = require("./ui/badge/badge");
var _boxArrow = require("./ui/box-arrow/box-arrow");
var _button = require("./ui/button/button");
var _buttonGroup = require("./ui/button/button-group");
var _buttonPin = require("./ui/button/button-pin");
var _buttonSquare = require("./ui/button/button-square");
var _card = require("./ui/card/card");
var _checkbox = require("./ui/checkbox/checkbox");
var _input = require("./ui/input/input");
var _inputDate = require("./ui/input/input-date");
var _inputNumber = require("./ui/input/input-number");
var _inputNumberCenter = require("./ui/input/input-number-center");
var _inputRadio = require("./ui/input/input-radio");
var _inputTag = require("./ui/input/input-tag");
var _menu = require("./ui/menu/menu");
var _progressBar = require("./ui/progress/progress-bar");
var _progressCircle = require("./ui/progress/progress-circle");
var _sidebar = require("./ui/sidebar/sidebar");
var _switch = require("./ui/switch/switch");
var _tab = require("./ui/tab/tab");
var _table = require("./ui/table/table");
var _tag = require("./ui/tag/tag");
var _tagx = require("./ui/tag/tagx");

},{"./style":"72rKO","@nitipit/adapter/src/adapter":"1Fra8","./ui/badge/badge":"hRUly","./ui/box-arrow/box-arrow":"lPBya","./ui/button/button":"3NusC","./ui/button/button-group":"808uY","./ui/button/button-pin":"5ibGP","./ui/button/button-square":"eKEy4","./ui/card/card":"iMJm5","./ui/checkbox/checkbox":"hO2dk","./ui/input/input":"4HNBJ","./ui/input/input-date":"ecTia","./ui/input/input-number":"8bUj3","./ui/input/input-number-center":"6Sae6","./ui/input/input-radio":"hkfMk","./ui/input/input-tag":"9RCxA","./ui/menu/menu":"kupAp","./ui/progress/progress-bar":"2e4fD","./ui/progress/progress-circle":"2RkPm","./ui/sidebar/sidebar":"9iVgh","./ui/switch/switch":"gsIJA","./ui/tab/tab":"8Zzpz","./ui/table/table":"5egmO","./ui/tag/tag":"1o7hu","./ui/tag/tagx":"dovaj","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"72rKO":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "addStyle", ()=>(0, _addStyle.addStyle));
parcelHelpers.export(exports, "aspectRatio", ()=>(0, _aspectRatio.aspectRatio));
parcelHelpers.export(exports, "bgColor", ()=>(0, _bgColor.bgColor));
parcelHelpers.export(exports, "bgColorInt", ()=>(0, _bgColorInt.bgColorInt));
parcelHelpers.export(exports, "fontFluid", ()=>(0, _fontFluid.fontFluid));
parcelHelpers.export(exports, "lift", ()=>(0, _lift.lift));
var _addStyle = require("./style/add-style");
var _aspectRatio = require("./style/aspect-ratio");
var _bgColor = require("./style/bg-color");
var _bgColorInt = require("./style/bg-color-int");
var _fontFluid = require("./style/font-fluid");
var _lift = require("./style/lift");

},{"./style/add-style":"jkvY3","./style/aspect-ratio":"2D33e","./style/bg-color":"celAt","./style/bg-color-int":"ckzzz","./style/font-fluid":"g8Grc","./style/lift":"9caa5","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"jkvY3":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "addStyle", ()=>(0, _adapter.addStyle));
var _adapter = require("@nitipit/adapter/src/adapter");

},{"@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"1Fra8":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "addStyle", ()=>(0, _css.injectGlobal));
parcelHelpers.export(exports, "define", ()=>define);
parcelHelpers.export(exports, "StyleClass", ()=>StyleClass);
parcelHelpers.export(exports, "Adapter", ()=>Adapter);
var _css = require("@emotion/css");
const define = (tagName, Class = Adapter)=>{
    Class.define(tagName);
};
class StyleClass {
    static css(style = {}) {
        return "";
    }
    static style(style = {}) {
        return "";
    }
}
class Adapter extends HTMLElement {
    static #_ = (()=>{
        this.Style = StyleClass;
    })();
    static get tagName() {
        if (!this._tagName) throw `${this.name} hasn't been defined a tag name`;
        return this._tagName;
    }
    static set tagName(tagName) {
        this._tagName = tagName;
    }
    static define(tagName) {
        // To extends this function, sub-elements must be defined before call
        // this function as `super.define(tagName);`
        try {
            customElements.define(tagName, this);
        } catch (error) {
            if (error instanceof DOMException) {
                console.error(`DOMException: '${this.name}' ` + `has already been defined to tag '${this.tagName}'\n` + `${error.stack}`);
                return;
            }
        }
        this.tagName = tagName;
        this.initStyle();
    }
    static initStyle() {
        (0, _css.injectGlobal)`
        ${this.tagName} {
            all: unset;
        }`;
        if (!this.Style) return;
        (0, _css.injectGlobal)`
        ${this.tagName} {
            ${this.Style.css()}
        }`;
    }
    static tagStyle(style) {
        if (typeof style == "string") {
            (0, _css.injectGlobal)`
            ${this.tagName} {
                ${style}
            }`;
            return;
        }
        (0, _css.injectGlobal)`
        ${this.tagName} {
            ${this.Style.style(style)}
        }`;
    }
    static classStyle(class_, style) {
        if (typeof style == "string") (0, _css.injectGlobal)`
            ${this.tagName}.${class_} {
                ${style}
            }`;
        else if (typeof style == "object") (0, _css.injectGlobal)`
            ${this.tagName}.${class_} {
                ${this.Style.style(style)}
            }`;
    }
    static #_1 = (()=>{
        this.max_id = Math.pow(16, 4) - 1;
    })();
    static #_2 = (()=>{
        this.instance = {};
    })();
    static _generate_id() {
        return `adt-${Math.floor(Math.random() * this.max_id).toString(16)}`;
    }
    constructor(){
        super();
        this._class = this.constructor;
        let id = this._class._generate_id();
        while(id in this._class.instance)id = this._class._generate_id();
        this._class.instance[id] = true;
        this._id = id;
    }
    addStyle(style) {
        this.classList.add(this._id);
        let selector = this.classList.value.replace(/ /g, ".");
        if (typeof style == "string") (0, _css.injectGlobal)`
            ${this.tagName}.${selector} {
                ${style}
            }`;
        else if (typeof style == "object") (0, _css.injectGlobal)`
            ${this.tagName}.${selector} {
                ${this._class.Style.style(style)}
            }`;
    }
    notify(name, options) {
        const event = new CustomEvent(name, options);
        this.dispatchEvent(event);
    }
}

},{"@emotion/css":"gyRZs","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"gyRZs":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "cache", ()=>cache);
parcelHelpers.export(exports, "css", ()=>css);
parcelHelpers.export(exports, "cx", ()=>cx);
parcelHelpers.export(exports, "flush", ()=>flush);
parcelHelpers.export(exports, "getRegisteredStyles", ()=>getRegisteredStyles);
parcelHelpers.export(exports, "hydrate", ()=>hydrate);
parcelHelpers.export(exports, "injectGlobal", ()=>injectGlobal);
parcelHelpers.export(exports, "keyframes", ()=>keyframes);
parcelHelpers.export(exports, "merge", ()=>merge);
parcelHelpers.export(exports, "sheet", ()=>sheet);
var _emotionCssCreateInstanceEsmJs = require("../create-instance/dist/emotion-css-create-instance.esm.js");
var _emotionCssCreateInstanceEsmJsDefault = parcelHelpers.interopDefault(_emotionCssCreateInstanceEsmJs);
var _cache = require("@emotion/cache");
var _serialize = require("@emotion/serialize");
var _utils = require("@emotion/utils");
var _createEmotion = (0, _emotionCssCreateInstanceEsmJsDefault.default)({
    key: "css"
}), flush = _createEmotion.flush, hydrate = _createEmotion.hydrate, cx = _createEmotion.cx, merge = _createEmotion.merge, getRegisteredStyles = _createEmotion.getRegisteredStyles, injectGlobal = _createEmotion.injectGlobal, keyframes = _createEmotion.keyframes, css = _createEmotion.css, sheet = _createEmotion.sheet, cache = _createEmotion.cache;

},{"../create-instance/dist/emotion-css-create-instance.esm.js":"k89zX","@emotion/cache":"3Umtj","@emotion/serialize":"kS2E2","@emotion/utils":"6UI8e","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"k89zX":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>createEmotion);
var _cache = require("@emotion/cache");
var _cacheDefault = parcelHelpers.interopDefault(_cache);
var _serialize = require("@emotion/serialize");
var _utils = require("@emotion/utils");
function insertWithoutScoping(cache, serialized) {
    if (cache.inserted[serialized.name] === undefined) return cache.insert("", serialized, cache.sheet, true);
}
function merge(registered, css, className) {
    var registeredStyles = [];
    var rawClassName = (0, _utils.getRegisteredStyles)(registered, registeredStyles, className);
    if (registeredStyles.length < 2) return className;
    return rawClassName + css(registeredStyles);
}
var createEmotion = function createEmotion(options) {
    var cache = (0, _cacheDefault.default)(options); // $FlowFixMe
    cache.sheet.speedy = function(value) {
        if (this.ctr !== 0) throw new Error("speedy must be changed before any rules are inserted");
        this.isSpeedy = value;
    };
    cache.compat = true;
    var css = function css() {
        for(var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++)args[_key] = arguments[_key];
        var serialized = (0, _serialize.serializeStyles)(args, cache.registered, undefined);
        (0, _utils.insertStyles)(cache, serialized, false);
        return cache.key + "-" + serialized.name;
    };
    var keyframes = function keyframes() {
        for(var _len2 = arguments.length, args = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++)args[_key2] = arguments[_key2];
        var serialized = (0, _serialize.serializeStyles)(args, cache.registered);
        var animation = "animation-" + serialized.name;
        insertWithoutScoping(cache, {
            name: serialized.name,
            styles: "@keyframes " + animation + "{" + serialized.styles + "}"
        });
        return animation;
    };
    var injectGlobal = function injectGlobal() {
        for(var _len3 = arguments.length, args = new Array(_len3), _key3 = 0; _key3 < _len3; _key3++)args[_key3] = arguments[_key3];
        var serialized = (0, _serialize.serializeStyles)(args, cache.registered);
        insertWithoutScoping(cache, serialized);
    };
    var cx = function cx() {
        for(var _len4 = arguments.length, args = new Array(_len4), _key4 = 0; _key4 < _len4; _key4++)args[_key4] = arguments[_key4];
        return merge(cache.registered, css, classnames(args));
    };
    return {
        css: css,
        cx: cx,
        injectGlobal: injectGlobal,
        keyframes: keyframes,
        hydrate: function hydrate(ids) {
            ids.forEach(function(key) {
                cache.inserted[key] = true;
            });
        },
        flush: function flush() {
            cache.registered = {};
            cache.inserted = {};
            cache.sheet.flush();
        },
        // $FlowFixMe
        sheet: cache.sheet,
        cache: cache,
        getRegisteredStyles: (0, _utils.getRegisteredStyles).bind(null, cache.registered),
        merge: merge.bind(null, cache.registered, css)
    };
};
var classnames = function classnames(args) {
    var cls = "";
    for(var i = 0; i < args.length; i++){
        var arg = args[i];
        if (arg == null) continue;
        var toAdd = void 0;
        switch(typeof arg){
            case "boolean":
                break;
            case "object":
                if (Array.isArray(arg)) toAdd = classnames(arg);
                else {
                    toAdd = "";
                    for(var k in arg)if (arg[k] && k) {
                        toAdd && (toAdd += " ");
                        toAdd += k;
                    }
                }
                break;
            default:
                toAdd = arg;
        }
        if (toAdd) {
            cls && (cls += " ");
            cls += toAdd;
        }
    }
    return cls;
};

},{"@emotion/cache":"3Umtj","@emotion/serialize":"kS2E2","@emotion/utils":"6UI8e","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"3Umtj":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>createCache);
var _sheet = require("@emotion/sheet");
var _stylis = require("stylis");
var _weakMemoize = require("@emotion/weak-memoize");
var _memoize = require("@emotion/memoize");
var identifierWithPointTracking = function identifierWithPointTracking(begin, points, index) {
    var previous = 0;
    var character = 0;
    while(true){
        previous = character;
        character = (0, _stylis.peek)(); // &\f
        if (previous === 38 && character === 12) points[index] = 1;
        if ((0, _stylis.token)(character)) break;
        (0, _stylis.next)();
    }
    return (0, _stylis.slice)(begin, (0, _stylis.position));
};
var toRules = function toRules(parsed, points) {
    // pretend we've started with a comma
    var index = -1;
    var character = 44;
    do switch((0, _stylis.token)(character)){
        case 0:
            // &\f
            if (character === 38 && (0, _stylis.peek)() === 12) // this is not 100% correct, we don't account for literal sequences here - like for example quoted strings
            // stylis inserts \f after & to know when & where it should replace this sequence with the context selector
            // and when it should just concatenate the outer and inner selectors
            // it's very unlikely for this sequence to actually appear in a different context, so we just leverage this fact here
            points[index] = 1;
            parsed[index] += identifierWithPointTracking((0, _stylis.position) - 1, points, index);
            break;
        case 2:
            parsed[index] += (0, _stylis.delimit)(character);
            break;
        case 4:
            // comma
            if (character === 44) {
                // colon
                parsed[++index] = (0, _stylis.peek)() === 58 ? "&\f" : "";
                points[index] = parsed[index].length;
                break;
            }
        // fallthrough
        default:
            parsed[index] += (0, _stylis.from)(character);
    }
    while (character = (0, _stylis.next)());
    return parsed;
};
var getRules = function getRules(value, points) {
    return (0, _stylis.dealloc)(toRules((0, _stylis.alloc)(value), points));
}; // WeakSet would be more appropriate, but only WeakMap is supported in IE11
var fixedElements = /* #__PURE__ */ new WeakMap();
var compat = function compat(element) {
    if (element.type !== "rule" || !element.parent || // positive .length indicates that this rule contains pseudo
    // negative .length indicates that this rule has been already prefixed
    element.length < 1) return;
    var value = element.value, parent = element.parent;
    var isImplicitRule = element.column === parent.column && element.line === parent.line;
    while(parent.type !== "rule"){
        parent = parent.parent;
        if (!parent) return;
    } // short-circuit for the simplest case
    if (element.props.length === 1 && value.charCodeAt(0) !== 58 && !fixedElements.get(parent)) return;
     // if this is an implicitly inserted rule (the one eagerly inserted at the each new nested level)
    // then the props has already been manipulated beforehand as they that array is shared between it and its "rule parent"
    if (isImplicitRule) return;
    fixedElements.set(element, true);
    var points = [];
    var rules = getRules(value, points);
    var parentRules = parent.props;
    for(var i = 0, k = 0; i < rules.length; i++)for(var j = 0; j < parentRules.length; j++, k++)element.props[k] = points[i] ? rules[i].replace(/&\f/g, parentRules[j]) : parentRules[j] + " " + rules[i];
};
var removeLabel = function removeLabel(element) {
    if (element.type === "decl") {
        var value = element.value;
        if (value.charCodeAt(0) === 108 && // charcode for b
        value.charCodeAt(2) === 98) {
            // this ignores label
            element["return"] = "";
            element.value = "";
        }
    }
};
var ignoreFlag = "emotion-disable-server-rendering-unsafe-selector-warning-please-do-not-use-this-the-warning-exists-for-a-reason";
var isIgnoringComment = function isIgnoringComment(element) {
    return element.type === "comm" && element.children.indexOf(ignoreFlag) > -1;
};
var createUnsafeSelectorsAlarm = function createUnsafeSelectorsAlarm(cache) {
    return function(element, index, children) {
        if (element.type !== "rule" || cache.compat) return;
        var unsafePseudoClasses = element.value.match(/(:first|:nth|:nth-last)-child/g);
        if (unsafePseudoClasses) {
            var isNested = !!element.parent; // in nested rules comments become children of the "auto-inserted" rule and that's always the `element.parent`
            //
            // considering this input:
            // .a {
            //   .b /* comm */ {}
            //   color: hotpink;
            // }
            // we get output corresponding to this:
            // .a {
            //   & {
            //     /* comm */
            //     color: hotpink;
            //   }
            //   .b {}
            // }
            var commentContainer = isNested ? element.parent.children : children;
            for(var i = commentContainer.length - 1; i >= 0; i--){
                var node = commentContainer[i];
                if (node.line < element.line) break;
                 // it is quite weird but comments are *usually* put at `column: element.column - 1`
                // so we seek *from the end* for the node that is earlier than the rule's `element` and check that
                // this will also match inputs like this:
                // .a {
                //   /* comm */
                //   .b {}
                // }
                //
                // but that is fine
                //
                // it would be the easiest to change the placement of the comment to be the first child of the rule:
                // .a {
                //   .b { /* comm */ }
                // }
                // with such inputs we wouldn't have to search for the comment at all
                // TODO: consider changing this comment placement in the next major version
                if (node.column < element.column) {
                    if (isIgnoringComment(node)) return;
                    break;
                }
            }
            unsafePseudoClasses.forEach(function(unsafePseudoClass) {
                console.error('The pseudo class "' + unsafePseudoClass + '" is potentially unsafe when doing server-side rendering. Try changing it to "' + unsafePseudoClass.split("-child")[0] + '-of-type".');
            });
        }
    };
};
var isImportRule = function isImportRule(element) {
    return element.type.charCodeAt(1) === 105 && element.type.charCodeAt(0) === 64;
};
var isPrependedWithRegularRules = function isPrependedWithRegularRules(index, children) {
    for(var i = index - 1; i >= 0; i--){
        if (!isImportRule(children[i])) return true;
    }
    return false;
}; // use this to remove incorrect elements from further processing
// so they don't get handed to the `sheet` (or anything else)
// as that could potentially lead to additional logs which in turn could be overhelming to the user
var nullifyElement = function nullifyElement(element) {
    element.type = "";
    element.value = "";
    element["return"] = "";
    element.children = "";
    element.props = "";
};
var incorrectImportAlarm = function incorrectImportAlarm(element, index, children) {
    if (!isImportRule(element)) return;
    if (element.parent) {
        console.error("`@import` rules can't be nested inside other rules. Please move it to the top level and put it before regular rules. Keep in mind that they can only be used within global styles.");
        nullifyElement(element);
    } else if (isPrependedWithRegularRules(index, children)) {
        console.error("`@import` rules can't be after other rules. Please put your `@import` rules before your other rules.");
        nullifyElement(element);
    }
};
/* eslint-disable no-fallthrough */ function prefix(value, length) {
    switch((0, _stylis.hash)(value, length)){
        // color-adjust
        case 5103:
            return (0, _stylis.WEBKIT) + "print-" + value + value;
        // animation, animation-(delay|direction|duration|fill-mode|iteration-count|name|play-state|timing-function)
        case 5737:
        case 4201:
        case 3177:
        case 3433:
        case 1641:
        case 4457:
        case 2921:
        case 5572:
        case 6356:
        case 5844:
        case 3191:
        case 6645:
        case 3005:
        case 6391:
        case 5879:
        case 5623:
        case 6135:
        case 4599:
        case 4855:
        case 4215:
        case 6389:
        case 5109:
        case 5365:
        case 5621:
        case 3829:
            return (0, _stylis.WEBKIT) + value + value;
        // appearance, user-select, transform, hyphens, text-size-adjust
        case 5349:
        case 4246:
        case 4810:
        case 6968:
        case 2756:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MOZ) + value + (0, _stylis.MS) + value + value;
        // flex, flex-direction
        case 6828:
        case 4268:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + value + value;
        // order
        case 6165:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + "flex-" + value + value;
        // align-items
        case 5187:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.replace)(value, /(\w+).+(:[^]+)/, (0, _stylis.WEBKIT) + "box-$1$2" + (0, _stylis.MS) + "flex-$1$2") + value;
        // align-self
        case 5443:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + "flex-item-" + (0, _stylis.replace)(value, /flex-|-self/, "") + value;
        // align-content
        case 4675:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + "flex-line-pack" + (0, _stylis.replace)(value, /align-content|flex-|-self/, "") + value;
        // flex-shrink
        case 5548:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, "shrink", "negative") + value;
        // flex-basis
        case 5292:
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, "basis", "preferred-size") + value;
        // flex-grow
        case 6060:
            return (0, _stylis.WEBKIT) + "box-" + (0, _stylis.replace)(value, "-grow", "") + (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, "grow", "positive") + value;
        // transition
        case 4554:
            return (0, _stylis.WEBKIT) + (0, _stylis.replace)(value, /([^-])(transform)/g, "$1" + (0, _stylis.WEBKIT) + "$2") + value;
        // cursor
        case 6187:
            return (0, _stylis.replace)((0, _stylis.replace)((0, _stylis.replace)(value, /(zoom-|grab)/, (0, _stylis.WEBKIT) + "$1"), /(image-set)/, (0, _stylis.WEBKIT) + "$1"), value, "") + value;
        // background, background-image
        case 5495:
        case 3959:
            return (0, _stylis.replace)(value, /(image-set\([^]*)/, (0, _stylis.WEBKIT) + "$1" + "$`$1");
        // justify-content
        case 4968:
            return (0, _stylis.replace)((0, _stylis.replace)(value, /(.+:)(flex-)?(.*)/, (0, _stylis.WEBKIT) + "box-pack:$3" + (0, _stylis.MS) + "flex-pack:$3"), /s.+-b[^;]+/, "justify") + (0, _stylis.WEBKIT) + value + value;
        // (margin|padding)-inline-(start|end)
        case 4095:
        case 3583:
        case 4068:
        case 2532:
            return (0, _stylis.replace)(value, /(.+)-inline(.+)/, (0, _stylis.WEBKIT) + "$1$2") + value;
        // (min|max)?(width|height|inline-size|block-size)
        case 8116:
        case 7059:
        case 5753:
        case 5535:
        case 5445:
        case 5701:
        case 4933:
        case 4677:
        case 5533:
        case 5789:
        case 5021:
        case 4765:
            // stretch, max-content, min-content, fill-available
            if ((0, _stylis.strlen)(value) - 1 - length > 6) switch((0, _stylis.charat)(value, length + 1)){
                // (m)ax-content, (m)in-content
                case 109:
                    // -
                    if ((0, _stylis.charat)(value, length + 4) !== 45) break;
                // (f)ill-available, (f)it-content
                case 102:
                    return (0, _stylis.replace)(value, /(.+:)(.+)-([^]+)/, "$1" + (0, _stylis.WEBKIT) + "$2-$3" + "$1" + (0, _stylis.MOZ) + ((0, _stylis.charat)(value, length + 3) == 108 ? "$3" : "$2-$3")) + value;
                // (s)tretch
                case 115:
                    return ~(0, _stylis.indexof)(value, "stretch") ? prefix((0, _stylis.replace)(value, "stretch", "fill-available"), length) + value : value;
            }
            break;
        // position: sticky
        case 4949:
            // (s)ticky?
            if ((0, _stylis.charat)(value, length + 1) !== 115) break;
        // display: (flex|inline-flex)
        case 6444:
            switch((0, _stylis.charat)(value, (0, _stylis.strlen)(value) - 3 - (~(0, _stylis.indexof)(value, "!important") && 10))){
                // stic(k)y
                case 107:
                    return (0, _stylis.replace)(value, ":", ":" + (0, _stylis.WEBKIT)) + value;
                // (inline-)?fl(e)x
                case 101:
                    return (0, _stylis.replace)(value, /(.+:)([^;!]+)(;|!.+)?/, "$1" + (0, _stylis.WEBKIT) + ((0, _stylis.charat)(value, 14) === 45 ? "inline-" : "") + "box$3" + "$1" + (0, _stylis.WEBKIT) + "$2$3" + "$1" + (0, _stylis.MS) + "$2box$3") + value;
            }
            break;
        // writing-mode
        case 5936:
            switch((0, _stylis.charat)(value, length + 11)){
                // vertical-l(r)
                case 114:
                    return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, /[svh]\w+-[tblr]{2}/, "tb") + value;
                // vertical-r(l)
                case 108:
                    return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, /[svh]\w+-[tblr]{2}/, "tb-rl") + value;
                // horizontal(-)tb
                case 45:
                    return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + (0, _stylis.replace)(value, /[svh]\w+-[tblr]{2}/, "lr") + value;
            }
            return (0, _stylis.WEBKIT) + value + (0, _stylis.MS) + value + value;
    }
    return value;
}
var prefixer = function prefixer(element, index, children, callback) {
    if (element.length > -1) {
        if (!element["return"]) switch(element.type){
            case 0, _stylis.DECLARATION:
                element["return"] = prefix(element.value, element.length);
                break;
            case 0, _stylis.KEYFRAMES:
                return (0, _stylis.serialize)([
                    (0, _stylis.copy)(element, {
                        value: (0, _stylis.replace)(element.value, "@", "@" + (0, _stylis.WEBKIT))
                    })
                ], callback);
            case 0, _stylis.RULESET:
                if (element.length) return (0, _stylis.combine)(element.props, function(value) {
                    switch((0, _stylis.match)(value, /(::plac\w+|:read-\w+)/)){
                        // :read-(only|write)
                        case ":read-only":
                        case ":read-write":
                            return (0, _stylis.serialize)([
                                (0, _stylis.copy)(element, {
                                    props: [
                                        (0, _stylis.replace)(value, /:(read-\w+)/, ":" + (0, _stylis.MOZ) + "$1")
                                    ]
                                })
                            ], callback);
                        // :placeholder
                        case "::placeholder":
                            return (0, _stylis.serialize)([
                                (0, _stylis.copy)(element, {
                                    props: [
                                        (0, _stylis.replace)(value, /:(plac\w+)/, ":" + (0, _stylis.WEBKIT) + "input-$1")
                                    ]
                                }),
                                (0, _stylis.copy)(element, {
                                    props: [
                                        (0, _stylis.replace)(value, /:(plac\w+)/, ":" + (0, _stylis.MOZ) + "$1")
                                    ]
                                }),
                                (0, _stylis.copy)(element, {
                                    props: [
                                        (0, _stylis.replace)(value, /:(plac\w+)/, (0, _stylis.MS) + "input-$1")
                                    ]
                                })
                            ], callback);
                    }
                    return "";
                });
        }
    }
};
var defaultStylisPlugins = [
    prefixer
];
var createCache = function createCache(options) {
    var key = options.key;
    if (!key) throw new Error("You have to configure `key` for your cache. Please make sure it's unique (and not equal to 'css') as it's used for linking styles to your cache.\nIf multiple caches share the same key they might \"fight\" for each other's style elements.");
    if (key === "css") {
        var ssrStyles = document.querySelectorAll("style[data-emotion]:not([data-s])"); // get SSRed styles out of the way of React's hydration
        // document.head is a safe place to move them to(though note document.head is not necessarily the last place they will be)
        // note this very very intentionally targets all style elements regardless of the key to ensure
        // that creating a cache works inside of render of a React component
        Array.prototype.forEach.call(ssrStyles, function(node) {
            // we want to only move elements which have a space in the data-emotion attribute value
            // because that indicates that it is an Emotion 11 server-side rendered style elements
            // while we will already ignore Emotion 11 client-side inserted styles because of the :not([data-s]) part in the selector
            // Emotion 10 client-side inserted styles did not have data-s (but importantly did not have a space in their data-emotion attributes)
            // so checking for the space ensures that loading Emotion 11 after Emotion 10 has inserted some styles
            // will not result in the Emotion 10 styles being destroyed
            var dataEmotionAttribute = node.getAttribute("data-emotion");
            if (dataEmotionAttribute.indexOf(" ") === -1) return;
            document.head.appendChild(node);
            node.setAttribute("data-s", "");
        });
    }
    var stylisPlugins = options.stylisPlugins || defaultStylisPlugins;
    // $FlowFixMe
    if (/[^a-z-]/.test(key)) throw new Error('Emotion key must only contain lower case alphabetical characters and - but "' + key + '" was passed');
    var inserted = {};
    var container;
    var nodesToHydrate = [];
    container = options.container || document.head;
    Array.prototype.forEach.call(// means that the style elements we're looking at are only Emotion 11 server-rendered style elements
    document.querySelectorAll('style[data-emotion^="' + key + ' "]'), function(node) {
        var attrib = node.getAttribute("data-emotion").split(" "); // $FlowFixMe
        for(var i = 1; i < attrib.length; i++)inserted[attrib[i]] = true;
        nodesToHydrate.push(node);
    });
    var _insert;
    var omnipresentPlugins = [
        compat,
        removeLabel
    ];
    omnipresentPlugins.push(createUnsafeSelectorsAlarm({
        get compat () {
            return cache.compat;
        }
    }), incorrectImportAlarm);
    var currentSheet;
    var finalizingPlugins = [
        (0, _stylis.stringify),
        function(element) {
            if (!element.root) {
                if (element["return"]) currentSheet.insert(element["return"]);
                else if (element.value && element.type !== (0, _stylis.COMMENT)) // insert empty rule in non-production environments
                // so @emotion/jest can grab `key` from the (JS)DOM for caches without any rules inserted yet
                currentSheet.insert(element.value + "{}");
            }
        }
    ];
    var serializer = (0, _stylis.middleware)(omnipresentPlugins.concat(stylisPlugins, finalizingPlugins));
    var stylis = function stylis(styles) {
        return (0, _stylis.serialize)((0, _stylis.compile)(styles), serializer);
    };
    _insert = function insert(selector, serialized, sheet, shouldCache) {
        currentSheet = sheet;
        if (serialized.map !== undefined) currentSheet = {
            insert: function insert(rule) {
                sheet.insert(rule + serialized.map);
            }
        };
        stylis(selector ? selector + "{" + serialized.styles + "}" : serialized.styles);
        if (shouldCache) cache.inserted[serialized.name] = true;
    };
    var cache = {
        key: key,
        sheet: new (0, _sheet.StyleSheet)({
            key: key,
            container: container,
            nonce: options.nonce,
            speedy: options.speedy,
            prepend: options.prepend,
            insertionPoint: options.insertionPoint
        }),
        nonce: options.nonce,
        inserted: inserted,
        registered: {},
        insert: _insert
    };
    cache.sheet.hydrate(nodesToHydrate);
    return cache;
};

},{"@emotion/sheet":"1BWeq","stylis":"bMCXt","@emotion/weak-memoize":"grJxk","@emotion/memoize":"2vzJd","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"1BWeq":[function(require,module,exports) {
/*

Based off glamor's StyleSheet, thanks Sunil ❤️

high performance StyleSheet for css-in-js systems

- uses multiple style tags behind the scenes for millions of rules
- uses `insertRule` for appending in production for *much* faster performance

// usage

import { StyleSheet } from '@emotion/sheet'

let styleSheet = new StyleSheet({ key: '', container: document.head })

styleSheet.insert('#box { border: 1px solid red; }')
- appends a css rule into the stylesheet

styleSheet.flush()
- empties the stylesheet of all its contents

*/ // $FlowFixMe
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "StyleSheet", ()=>StyleSheet);
function sheetForTag(tag) {
    if (tag.sheet) // $FlowFixMe
    return tag.sheet;
     // this weirdness brought to you by firefox
    /* istanbul ignore next */ for(var i = 0; i < document.styleSheets.length; i++){
        if (document.styleSheets[i].ownerNode === tag) // $FlowFixMe
        return document.styleSheets[i];
    }
}
function createStyleElement(options) {
    var tag = document.createElement("style");
    tag.setAttribute("data-emotion", options.key);
    if (options.nonce !== undefined) tag.setAttribute("nonce", options.nonce);
    tag.appendChild(document.createTextNode(""));
    tag.setAttribute("data-s", "");
    return tag;
}
var StyleSheet = /*#__PURE__*/ function() {
    // Using Node instead of HTMLElement since container may be a ShadowRoot
    function StyleSheet(options) {
        var _this = this;
        this._insertTag = function(tag) {
            var before;
            if (_this.tags.length === 0) {
                if (_this.insertionPoint) before = _this.insertionPoint.nextSibling;
                else if (_this.prepend) before = _this.container.firstChild;
                else before = _this.before;
            } else before = _this.tags[_this.tags.length - 1].nextSibling;
            _this.container.insertBefore(tag, before);
            _this.tags.push(tag);
        };
        this.isSpeedy = options.speedy === undefined ? false : options.speedy;
        this.tags = [];
        this.ctr = 0;
        this.nonce = options.nonce; // key is the value of the data-emotion attribute, it's used to identify different sheets
        this.key = options.key;
        this.container = options.container;
        this.prepend = options.prepend;
        this.insertionPoint = options.insertionPoint;
        this.before = null;
    }
    var _proto = StyleSheet.prototype;
    _proto.hydrate = function hydrate(nodes) {
        nodes.forEach(this._insertTag);
    };
    _proto.insert = function insert(rule) {
        // the max length is how many rules we have per style tag, it's 65000 in speedy mode
        // it's 1 in dev because we insert source maps that map a single rule to a location
        // and you can only have one source map per style tag
        if (this.ctr % (this.isSpeedy ? 65000 : 1) === 0) this._insertTag(createStyleElement(this));
        var tag = this.tags[this.tags.length - 1];
        var isImportRule = rule.charCodeAt(0) === 64 && rule.charCodeAt(1) === 105;
        if (isImportRule && this._alreadyInsertedOrderInsensitiveRule) // this would only cause problem in speedy mode
        // but we don't want enabling speedy to affect the observable behavior
        // so we report this error at all times
        console.error("You're attempting to insert the following rule:\n" + rule + "\n\n`@import` rules must be before all other types of rules in a stylesheet but other rules have already been inserted. Please ensure that `@import` rules are before all other rules.");
        this._alreadyInsertedOrderInsensitiveRule = this._alreadyInsertedOrderInsensitiveRule || !isImportRule;
        if (this.isSpeedy) {
            var sheet = sheetForTag(tag);
            try {
                // this is the ultrafast version, works across browsers
                // the big drawback is that the css won't be editable in devtools
                sheet.insertRule(rule, sheet.cssRules.length);
            } catch (e) {
                if (!/:(-moz-placeholder|-moz-focus-inner|-moz-focusring|-ms-input-placeholder|-moz-read-write|-moz-read-only|-ms-clear|-ms-expand|-ms-reveal){/.test(rule)) console.error('There was a problem inserting the following rule: "' + rule + '"', e);
            }
        } else tag.appendChild(document.createTextNode(rule));
        this.ctr++;
    };
    _proto.flush = function flush() {
        // $FlowFixMe
        this.tags.forEach(function(tag) {
            return tag.parentNode && tag.parentNode.removeChild(tag);
        });
        this.tags = [];
        this.ctr = 0;
        this._alreadyInsertedOrderInsensitiveRule = false;
    };
    return StyleSheet;
}();

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"gkKU3":[function(require,module,exports) {
exports.interopDefault = function(a) {
    return a && a.__esModule ? a : {
        default: a
    };
};
exports.defineInteropFlag = function(a) {
    Object.defineProperty(a, "__esModule", {
        value: true
    });
};
exports.exportAll = function(source, dest) {
    Object.keys(source).forEach(function(key) {
        if (key === "default" || key === "__esModule" || dest.hasOwnProperty(key)) return;
        Object.defineProperty(dest, key, {
            enumerable: true,
            get: function() {
                return source[key];
            }
        });
    });
    return dest;
};
exports.export = function(dest, destName, get) {
    Object.defineProperty(dest, destName, {
        enumerable: true,
        get: get
    });
};

},{}],"bMCXt":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "CHARSET", ()=>f);
parcelHelpers.export(exports, "COMMENT", ()=>n);
parcelHelpers.export(exports, "COUNTER_STYLE", ()=>w);
parcelHelpers.export(exports, "DECLARATION", ()=>s);
parcelHelpers.export(exports, "DOCUMENT", ()=>v);
parcelHelpers.export(exports, "FONT_FACE", ()=>b);
parcelHelpers.export(exports, "FONT_FEATURE_VALUES", ()=>d);
parcelHelpers.export(exports, "IMPORT", ()=>i);
parcelHelpers.export(exports, "KEYFRAMES", ()=>h);
parcelHelpers.export(exports, "LAYER", ()=>$);
parcelHelpers.export(exports, "MEDIA", ()=>u);
parcelHelpers.export(exports, "MOZ", ()=>r);
parcelHelpers.export(exports, "MS", ()=>e);
parcelHelpers.export(exports, "NAMESPACE", ()=>p);
parcelHelpers.export(exports, "PAGE", ()=>t);
parcelHelpers.export(exports, "RULESET", ()=>c);
parcelHelpers.export(exports, "SUPPORTS", ()=>l);
parcelHelpers.export(exports, "VIEWPORT", ()=>o);
parcelHelpers.export(exports, "WEBKIT", ()=>a);
parcelHelpers.export(exports, "abs", ()=>g);
parcelHelpers.export(exports, "alloc", ()=>V);
parcelHelpers.export(exports, "append", ()=>q);
parcelHelpers.export(exports, "assign", ()=>m);
parcelHelpers.export(exports, "caret", ()=>R);
parcelHelpers.export(exports, "char", ()=>L);
parcelHelpers.export(exports, "character", ()=>H);
parcelHelpers.export(exports, "characters", ()=>I);
parcelHelpers.export(exports, "charat", ()=>O);
parcelHelpers.export(exports, "column", ()=>E);
parcelHelpers.export(exports, "combine", ()=>B);
parcelHelpers.export(exports, "comment", ()=>ue);
parcelHelpers.export(exports, "commenter", ()=>ae);
parcelHelpers.export(exports, "compile", ()=>ce);
parcelHelpers.export(exports, "copy", ()=>K);
parcelHelpers.export(exports, "dealloc", ()=>W);
parcelHelpers.export(exports, "declaration", ()=>ie);
parcelHelpers.export(exports, "delimit", ()=>X);
parcelHelpers.export(exports, "delimiter", ()=>re);
parcelHelpers.export(exports, "escaping", ()=>ee);
parcelHelpers.export(exports, "from", ()=>k);
parcelHelpers.export(exports, "hash", ()=>x);
parcelHelpers.export(exports, "identifier", ()=>ne);
parcelHelpers.export(exports, "indexof", ()=>C);
parcelHelpers.export(exports, "length", ()=>F);
parcelHelpers.export(exports, "line", ()=>D);
parcelHelpers.export(exports, "match", ()=>j);
parcelHelpers.export(exports, "middleware", ()=>ve);
parcelHelpers.export(exports, "namespace", ()=>be);
parcelHelpers.export(exports, "next", ()=>P);
parcelHelpers.export(exports, "node", ()=>J);
parcelHelpers.export(exports, "parse", ()=>se);
parcelHelpers.export(exports, "peek", ()=>Q);
parcelHelpers.export(exports, "position", ()=>G);
parcelHelpers.export(exports, "prefix", ()=>fe);
parcelHelpers.export(exports, "prefixer", ()=>he);
parcelHelpers.export(exports, "prev", ()=>N);
parcelHelpers.export(exports, "replace", ()=>z);
parcelHelpers.export(exports, "ruleset", ()=>te);
parcelHelpers.export(exports, "rulesheet", ()=>pe);
parcelHelpers.export(exports, "serialize", ()=>oe);
parcelHelpers.export(exports, "sizeof", ()=>S);
parcelHelpers.export(exports, "slice", ()=>T);
parcelHelpers.export(exports, "stringify", ()=>le);
parcelHelpers.export(exports, "strlen", ()=>M);
parcelHelpers.export(exports, "substr", ()=>A);
parcelHelpers.export(exports, "token", ()=>U);
parcelHelpers.export(exports, "tokenize", ()=>Y);
parcelHelpers.export(exports, "tokenizer", ()=>_);
parcelHelpers.export(exports, "trim", ()=>y);
parcelHelpers.export(exports, "whitespace", ()=>Z);
var e = "-ms-";
var r = "-moz-";
var a = "-webkit-";
var n = "comm";
var c = "rule";
var s = "decl";
var t = "@page";
var u = "@media";
var i = "@import";
var f = "@charset";
var o = "@viewport";
var l = "@supports";
var v = "@document";
var p = "@namespace";
var h = "@keyframes";
var b = "@font-face";
var w = "@counter-style";
var d = "@font-feature-values";
var $ = "@layer";
var g = Math.abs;
var k = String.fromCharCode;
var m = Object.assign;
function x(e, r) {
    return O(e, 0) ^ 45 ? (((r << 2 ^ O(e, 0)) << 2 ^ O(e, 1)) << 2 ^ O(e, 2)) << 2 ^ O(e, 3) : 0;
}
function y(e) {
    return e.trim();
}
function j(e, r) {
    return (e = r.exec(e)) ? e[0] : e;
}
function z(e, r, a) {
    return e.replace(r, a);
}
function C(e, r) {
    return e.indexOf(r);
}
function O(e, r) {
    return e.charCodeAt(r) | 0;
}
function A(e, r, a) {
    return e.slice(r, a);
}
function M(e) {
    return e.length;
}
function S(e) {
    return e.length;
}
function q(e, r) {
    return r.push(e), e;
}
function B(e, r) {
    return e.map(r).join("");
}
var D = 1;
var E = 1;
var F = 0;
var G = 0;
var H = 0;
var I = "";
function J(e, r, a, n, c, s, t) {
    return {
        value: e,
        root: r,
        parent: a,
        type: n,
        props: c,
        children: s,
        line: D,
        column: E,
        length: t,
        return: ""
    };
}
function K(e, r) {
    return m(J("", null, null, "", null, null, 0), e, {
        length: -e.length
    }, r);
}
function L() {
    return H;
}
function N() {
    H = G > 0 ? O(I, --G) : 0;
    if (E--, H === 10) E = 1, D--;
    return H;
}
function P() {
    H = G < F ? O(I, G++) : 0;
    if (E++, H === 10) E = 1, D++;
    return H;
}
function Q() {
    return O(I, G);
}
function R() {
    return G;
}
function T(e, r) {
    return A(I, e, r);
}
function U(e) {
    switch(e){
        case 0:
        case 9:
        case 10:
        case 13:
        case 32:
            return 5;
        case 33:
        case 43:
        case 44:
        case 47:
        case 62:
        case 64:
        case 126:
        case 59:
        case 123:
        case 125:
            return 4;
        case 58:
            return 3;
        case 34:
        case 39:
        case 40:
        case 91:
            return 2;
        case 41:
        case 93:
            return 1;
    }
    return 0;
}
function V(e) {
    return D = E = 1, F = M(I = e), G = 0, [];
}
function W(e) {
    return I = "", e;
}
function X(e) {
    return y(T(G - 1, re(e === 91 ? e + 2 : e === 40 ? e + 1 : e)));
}
function Y(e) {
    return W(_(V(e)));
}
function Z(e) {
    while(H = Q())if (H < 33) P();
    else break;
    return U(e) > 2 || U(H) > 3 ? "" : " ";
}
function _(e) {
    while(P())switch(U(H)){
        case 0:
            q(ne(G - 1), e);
            break;
        case 2:
            q(X(H), e);
            break;
        default:
            q(k(H), e);
    }
    return e;
}
function ee(e, r) {
    while(--r && P())if (H < 48 || H > 102 || H > 57 && H < 65 || H > 70 && H < 97) break;
    return T(e, R() + (r < 6 && Q() == 32 && P() == 32));
}
function re(e) {
    while(P())switch(H){
        case e:
            return G;
        case 34:
        case 39:
            if (e !== 34 && e !== 39) re(H);
            break;
        case 40:
            if (e === 41) re(e);
            break;
        case 92:
            P();
            break;
    }
    return G;
}
function ae(e, r) {
    while(P())if (e + H === 57) break;
    else if (e + H === 84 && Q() === 47) break;
    return "/*" + T(r, G - 1) + "*" + k(e === 47 ? e : P());
}
function ne(e) {
    while(!U(Q()))P();
    return T(e, G);
}
function ce(e) {
    return W(se("", null, null, null, [
        ""
    ], e = V(e), 0, [
        0
    ], e));
}
function se(e, r, a, n, c, s, t, u, i) {
    var f = 0;
    var o = 0;
    var l = t;
    var v = 0;
    var p = 0;
    var h = 0;
    var b = 1;
    var w = 1;
    var d = 1;
    var $ = 0;
    var g = "";
    var m = c;
    var x = s;
    var y = n;
    var j = g;
    while(w)switch(h = $, $ = P()){
        case 40:
            if (h != 108 && O(j, l - 1) == 58) {
                if (C(j += z(X($), "&", "&\f"), "&\f") != -1) d = -1;
                break;
            }
        case 34:
        case 39:
        case 91:
            j += X($);
            break;
        case 9:
        case 10:
        case 13:
        case 32:
            j += Z(h);
            break;
        case 92:
            j += ee(R() - 1, 7);
            continue;
        case 47:
            switch(Q()){
                case 42:
                case 47:
                    q(ue(ae(P(), R()), r, a), i);
                    break;
                default:
                    j += "/";
            }
            break;
        case 123 * b:
            u[f++] = M(j) * d;
        case 125 * b:
        case 59:
        case 0:
            switch($){
                case 0:
                case 125:
                    w = 0;
                case 59 + o:
                    if (d == -1) j = z(j, /\f/g, "");
                    if (p > 0 && M(j) - l) q(p > 32 ? ie(j + ";", n, a, l - 1) : ie(z(j, " ", "") + ";", n, a, l - 2), i);
                    break;
                case 59:
                    j += ";";
                default:
                    q(y = te(j, r, a, f, o, c, u, g, m = [], x = [], l), s);
                    if ($ === 123) {
                        if (o === 0) se(j, r, y, y, m, s, l, u, x);
                        else switch(v === 99 && O(j, 3) === 110 ? 100 : v){
                            case 100:
                            case 108:
                            case 109:
                            case 115:
                                se(e, y, y, n && q(te(e, y, y, 0, 0, c, u, g, c, m = [], l), x), c, x, l, u, n ? m : x);
                                break;
                            default:
                                se(j, y, y, y, [
                                    ""
                                ], x, 0, u, x);
                        }
                    }
            }
            f = o = p = 0, b = d = 1, g = j = "", l = t;
            break;
        case 58:
            l = 1 + M(j), p = h;
        default:
            if (b < 1) {
                if ($ == 123) --b;
                else if ($ == 125 && b++ == 0 && N() == 125) continue;
            }
            switch(j += k($), $ * b){
                case 38:
                    d = o > 0 ? 1 : (j += "\f", -1);
                    break;
                case 44:
                    u[f++] = (M(j) - 1) * d, d = 1;
                    break;
                case 64:
                    if (Q() === 45) j += X(P());
                    v = Q(), o = l = M(g = j += ne(R())), $++;
                    break;
                case 45:
                    if (h === 45 && M(j) == 2) b = 0;
            }
    }
    return s;
}
function te(e, r, a, n, s, t, u, i, f, o, l) {
    var v = s - 1;
    var p = s === 0 ? t : [
        ""
    ];
    var h = S(p);
    for(var b = 0, w = 0, d = 0; b < n; ++b)for(var $ = 0, k = A(e, v + 1, v = g(w = u[b])), m = e; $ < h; ++$)if (m = y(w > 0 ? p[$] + " " + k : z(k, /&\f/g, p[$]))) f[d++] = m;
    return J(e, r, a, s === 0 ? c : i, f, o, l);
}
function ue(e, r, a) {
    return J(e, r, a, n, k(L()), A(e, 2, -2), 0);
}
function ie(e, r, a, n) {
    return J(e, r, a, s, A(e, 0, n), A(e, n + 1, -1), n);
}
function fe(n, c, s) {
    switch(x(n, c)){
        case 5103:
            return a + "print-" + n + n;
        case 5737:
        case 4201:
        case 3177:
        case 3433:
        case 1641:
        case 4457:
        case 2921:
        case 5572:
        case 6356:
        case 5844:
        case 3191:
        case 6645:
        case 3005:
        case 6391:
        case 5879:
        case 5623:
        case 6135:
        case 4599:
        case 4855:
        case 4215:
        case 6389:
        case 5109:
        case 5365:
        case 5621:
        case 3829:
            return a + n + n;
        case 4789:
            return r + n + n;
        case 5349:
        case 4246:
        case 4810:
        case 6968:
        case 2756:
            return a + n + r + n + e + n + n;
        case 5936:
            switch(O(n, c + 11)){
                case 114:
                    return a + n + e + z(n, /[svh]\w+-[tblr]{2}/, "tb") + n;
                case 108:
                    return a + n + e + z(n, /[svh]\w+-[tblr]{2}/, "tb-rl") + n;
                case 45:
                    return a + n + e + z(n, /[svh]\w+-[tblr]{2}/, "lr") + n;
            }
        case 6828:
        case 4268:
        case 2903:
            return a + n + e + n + n;
        case 6165:
            return a + n + e + "flex-" + n + n;
        case 5187:
            return a + n + z(n, /(\w+).+(:[^]+)/, a + "box-$1$2" + e + "flex-$1$2") + n;
        case 5443:
            return a + n + e + "flex-item-" + z(n, /flex-|-self/g, "") + (!j(n, /flex-|baseline/) ? e + "grid-row-" + z(n, /flex-|-self/g, "") : "") + n;
        case 4675:
            return a + n + e + "flex-line-pack" + z(n, /align-content|flex-|-self/g, "") + n;
        case 5548:
            return a + n + e + z(n, "shrink", "negative") + n;
        case 5292:
            return a + n + e + z(n, "basis", "preferred-size") + n;
        case 6060:
            return a + "box-" + z(n, "-grow", "") + a + n + e + z(n, "grow", "positive") + n;
        case 4554:
            return a + z(n, /([^-])(transform)/g, "$1" + a + "$2") + n;
        case 6187:
            return z(z(z(n, /(zoom-|grab)/, a + "$1"), /(image-set)/, a + "$1"), n, "") + n;
        case 5495:
        case 3959:
            return z(n, /(image-set\([^]*)/, a + "$1" + "$`$1");
        case 4968:
            return z(z(n, /(.+:)(flex-)?(.*)/, a + "box-pack:$3" + e + "flex-pack:$3"), /s.+-b[^;]+/, "justify") + a + n + n;
        case 4200:
            if (!j(n, /flex-|baseline/)) return e + "grid-column-align" + A(n, c) + n;
            break;
        case 2592:
        case 3360:
            return e + z(n, "template-", "") + n;
        case 4384:
        case 3616:
            if (s && s.some(function(e, r) {
                return c = r, j(e.props, /grid-\w+-end/);
            })) return ~C(n + (s = s[c].value), "span") ? n : e + z(n, "-start", "") + n + e + "grid-row-span:" + (~C(s, "span") ? j(s, /\d+/) : +j(s, /\d+/) - +j(n, /\d+/)) + ";";
            return e + z(n, "-start", "") + n;
        case 4896:
        case 4128:
            return s && s.some(function(e) {
                return j(e.props, /grid-\w+-start/);
            }) ? n : e + z(z(n, "-end", "-span"), "span ", "") + n;
        case 4095:
        case 3583:
        case 4068:
        case 2532:
            return z(n, /(.+)-inline(.+)/, a + "$1$2") + n;
        case 8116:
        case 7059:
        case 5753:
        case 5535:
        case 5445:
        case 5701:
        case 4933:
        case 4677:
        case 5533:
        case 5789:
        case 5021:
        case 4765:
            if (M(n) - 1 - c > 6) switch(O(n, c + 1)){
                case 109:
                    if (O(n, c + 4) !== 45) break;
                case 102:
                    return z(n, /(.+:)(.+)-([^]+)/, "$1" + a + "$2-$3" + "$1" + r + (O(n, c + 3) == 108 ? "$3" : "$2-$3")) + n;
                case 115:
                    return ~C(n, "stretch") ? fe(z(n, "stretch", "fill-available"), c, s) + n : n;
            }
            break;
        case 5152:
        case 5920:
            return z(n, /(.+?):(\d+)(\s*\/\s*(span)?\s*(\d+))?(.*)/, function(r, a, c, s, t, u, i) {
                return e + a + ":" + c + i + (s ? e + a + "-span:" + (t ? u : +u - +c) + i : "") + n;
            });
        case 4949:
            if (O(n, c + 6) === 121) return z(n, ":", ":" + a) + n;
            break;
        case 6444:
            switch(O(n, O(n, 14) === 45 ? 18 : 11)){
                case 120:
                    return z(n, /(.+:)([^;\s!]+)(;|(\s+)?!.+)?/, "$1" + a + (O(n, 14) === 45 ? "inline-" : "") + "box$3" + "$1" + a + "$2$3" + "$1" + e + "$2box$3") + n;
                case 100:
                    return z(n, ":", ":" + e) + n;
            }
            break;
        case 5719:
        case 2647:
        case 2135:
        case 3927:
        case 2391:
            return z(n, "scroll-", "scroll-snap-") + n;
    }
    return n;
}
function oe(e, r) {
    var a = "";
    var n = S(e);
    for(var c = 0; c < n; c++)a += r(e[c], c, e, r) || "";
    return a;
}
function le(e, r, a, t) {
    switch(e.type){
        case $:
            if (e.children.length) break;
        case i:
        case s:
            return e.return = e.return || e.value;
        case n:
            return "";
        case h:
            return e.return = e.value + "{" + oe(e.children, t) + "}";
        case c:
            e.value = e.props.join(",");
    }
    return M(a = oe(e.children, t)) ? e.return = e.value + "{" + a + "}" : "";
}
function ve(e) {
    var r = S(e);
    return function(a, n, c, s) {
        var t = "";
        for(var u = 0; u < r; u++)t += e[u](a, n, c, s) || "";
        return t;
    };
}
function pe(e) {
    return function(r) {
        if (!r.root) {
            if (r = r.return) e(r);
        }
    };
}
function he(n, t, u, i) {
    if (n.length > -1) {
        if (!n.return) switch(n.type){
            case s:
                n.return = fe(n.value, n.length, u);
                return;
            case h:
                return oe([
                    K(n, {
                        value: z(n.value, "@", "@" + a)
                    })
                ], i);
            case c:
                if (n.length) return B(n.props, function(c) {
                    switch(j(c, /(::plac\w+|:read-\w+)/)){
                        case ":read-only":
                        case ":read-write":
                            return oe([
                                K(n, {
                                    props: [
                                        z(c, /:(read-\w+)/, ":" + r + "$1")
                                    ]
                                })
                            ], i);
                        case "::placeholder":
                            return oe([
                                K(n, {
                                    props: [
                                        z(c, /:(plac\w+)/, ":" + a + "input-$1")
                                    ]
                                }),
                                K(n, {
                                    props: [
                                        z(c, /:(plac\w+)/, ":" + r + "$1")
                                    ]
                                }),
                                K(n, {
                                    props: [
                                        z(c, /:(plac\w+)/, e + "input-$1")
                                    ]
                                })
                            ], i);
                    }
                    return "";
                });
        }
    }
}
function be(e) {
    switch(e.type){
        case c:
            e.props = e.props.map(function(r) {
                return B(Y(r), function(r, a, n) {
                    switch(O(r, 0)){
                        case 12:
                            return A(r, 1, M(r));
                        case 0:
                        case 40:
                        case 43:
                        case 62:
                        case 126:
                            return r;
                        case 58:
                            if (n[++a] === "global") n[a] = "", n[++a] = "\f" + A(n[a], a = 1, -1);
                        case 32:
                            return a === 1 ? "" : r;
                        default:
                            switch(a){
                                case 0:
                                    e = r;
                                    return S(n) > 1 ? "" : r;
                                case a = S(n) - 1:
                                case 2:
                                    return a === 2 ? r + e + e : r + e;
                                default:
                                    return r;
                            }
                    }
                });
            });
    }
}

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"grJxk":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>weakMemoize);
var weakMemoize = function weakMemoize(func) {
    // $FlowFixMe flow doesn't include all non-primitive types as allowed for weakmaps
    var cache = new WeakMap();
    return function(arg) {
        if (cache.has(arg)) // $FlowFixMe
        return cache.get(arg);
        var ret = func(arg);
        cache.set(arg, ret);
        return ret;
    };
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2vzJd":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>memoize);
function memoize(fn) {
    var cache = Object.create(null);
    return function(arg) {
        if (cache[arg] === undefined) cache[arg] = fn(arg);
        return cache[arg];
    };
}

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"kS2E2":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "serializeStyles", ()=>serializeStyles);
var _hash = require("@emotion/hash");
var _hashDefault = parcelHelpers.interopDefault(_hash);
var _unitless = require("@emotion/unitless");
var _unitlessDefault = parcelHelpers.interopDefault(_unitless);
var _memoize = require("@emotion/memoize");
var _memoizeDefault = parcelHelpers.interopDefault(_memoize);
var ILLEGAL_ESCAPE_SEQUENCE_ERROR = "You have illegal escape sequence in your template literal, most likely inside content's property value.\nBecause you write your CSS inside a JavaScript string you actually have to do double escaping, so for example \"content: '\\00d7';\" should become \"content: '\\\\00d7';\".\nYou can read more about this here:\nhttps://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#ES2018_revision_of_illegal_escape_sequences";
var UNDEFINED_AS_OBJECT_KEY_ERROR = "You have passed in falsy value as style object's key (can happen when in example you pass unexported component as computed key).";
var hyphenateRegex = /[A-Z]|^ms/g;
var animationRegex = /_EMO_([^_]+?)_([^]*?)_EMO_/g;
var isCustomProperty = function isCustomProperty(property) {
    return property.charCodeAt(1) === 45;
};
var isProcessableValue = function isProcessableValue(value) {
    return value != null && typeof value !== "boolean";
};
var processStyleName = /* #__PURE__ */ (0, _memoizeDefault.default)(function(styleName) {
    return isCustomProperty(styleName) ? styleName : styleName.replace(hyphenateRegex, "-$&").toLowerCase();
});
var processStyleValue = function processStyleValue(key, value) {
    switch(key){
        case "animation":
        case "animationName":
            if (typeof value === "string") return value.replace(animationRegex, function(match, p1, p2) {
                cursor = {
                    name: p1,
                    styles: p2,
                    next: cursor
                };
                return p1;
            });
    }
    if ((0, _unitlessDefault.default)[key] !== 1 && !isCustomProperty(key) && typeof value === "number" && value !== 0) return value + "px";
    return value;
};
var contentValuePattern = /(var|attr|counters?|url|element|(((repeating-)?(linear|radial))|conic)-gradient)\(|(no-)?(open|close)-quote/;
var contentValues = [
    "normal",
    "none",
    "initial",
    "inherit",
    "unset"
];
var oldProcessStyleValue = processStyleValue;
var msPattern = /^-ms-/;
var hyphenPattern = /-(.)/g;
var hyphenatedCache = {};
processStyleValue = function processStyleValue(key, value) {
    if (key === "content") {
        if (typeof value !== "string" || contentValues.indexOf(value) === -1 && !contentValuePattern.test(value) && (value.charAt(0) !== value.charAt(value.length - 1) || value.charAt(0) !== '"' && value.charAt(0) !== "'")) throw new Error("You seem to be using a value for 'content' without quotes, try replacing it with `content: '\"" + value + "\"'`");
    }
    var processed = oldProcessStyleValue(key, value);
    if (processed !== "" && !isCustomProperty(key) && key.indexOf("-") !== -1 && hyphenatedCache[key] === undefined) {
        hyphenatedCache[key] = true;
        console.error("Using kebab-case for css properties in objects is not supported. Did you mean " + key.replace(msPattern, "ms-").replace(hyphenPattern, function(str, _char) {
            return _char.toUpperCase();
        }) + "?");
    }
    return processed;
};
var noComponentSelectorMessage = "Component selectors can only be used in conjunction with @emotion/babel-plugin, the swc Emotion plugin, or another Emotion-aware compiler transform.";
function handleInterpolation(mergedProps, registered, interpolation) {
    if (interpolation == null) return "";
    if (interpolation.__emotion_styles !== undefined) {
        if (interpolation.toString() === "NO_COMPONENT_SELECTOR") throw new Error(noComponentSelectorMessage);
        return interpolation;
    }
    switch(typeof interpolation){
        case "boolean":
            return "";
        case "object":
            if (interpolation.anim === 1) {
                cursor = {
                    name: interpolation.name,
                    styles: interpolation.styles,
                    next: cursor
                };
                return interpolation.name;
            }
            if (interpolation.styles !== undefined) {
                var next = interpolation.next;
                if (next !== undefined) // not the most efficient thing ever but this is a pretty rare case
                // and there will be very few iterations of this generally
                while(next !== undefined){
                    cursor = {
                        name: next.name,
                        styles: next.styles,
                        next: cursor
                    };
                    next = next.next;
                }
                var styles = interpolation.styles + ";";
                if (interpolation.map !== undefined) styles += interpolation.map;
                return styles;
            }
            return createStringFromObject(mergedProps, registered, interpolation);
        case "function":
            if (mergedProps !== undefined) {
                var previousCursor = cursor;
                var result = interpolation(mergedProps);
                cursor = previousCursor;
                return handleInterpolation(mergedProps, registered, result);
            } else console.error("Functions that are interpolated in css calls will be stringified.\nIf you want to have a css call based on props, create a function that returns a css call like this\nlet dynamicStyle = (props) => css`color: ${props.color}`\nIt can be called directly with props or interpolated in a styled call like this\nlet SomeComponent = styled('div')`${dynamicStyle}`");
            break;
        case "string":
            var matched = [];
            var replaced = interpolation.replace(animationRegex, function(match, p1, p2) {
                var fakeVarName = "animation" + matched.length;
                matched.push("const " + fakeVarName + " = keyframes`" + p2.replace(/^@keyframes animation-\w+/, "") + "`");
                return "${" + fakeVarName + "}";
            });
            if (matched.length) console.error("`keyframes` output got interpolated into plain string, please wrap it with `css`.\n\nInstead of doing this:\n\n" + [].concat(matched, [
                "`" + replaced + "`"
            ]).join("\n") + "\n\nYou should wrap it with `css` like this:\n\n" + ("css`" + replaced + "`"));
            break;
    } // finalize string values (regular strings and functions interpolated into css calls)
    if (registered == null) return interpolation;
    var cached = registered[interpolation];
    return cached !== undefined ? cached : interpolation;
}
function createStringFromObject(mergedProps, registered, obj) {
    var string = "";
    if (Array.isArray(obj)) for(var i = 0; i < obj.length; i++)string += handleInterpolation(mergedProps, registered, obj[i]) + ";";
    else for(var _key in obj){
        var value = obj[_key];
        if (typeof value !== "object") {
            if (registered != null && registered[value] !== undefined) string += _key + "{" + registered[value] + "}";
            else if (isProcessableValue(value)) string += processStyleName(_key) + ":" + processStyleValue(_key, value) + ";";
        } else {
            if (_key === "NO_COMPONENT_SELECTOR" && true) throw new Error(noComponentSelectorMessage);
            if (Array.isArray(value) && typeof value[0] === "string" && (registered == null || registered[value[0]] === undefined)) {
                for(var _i = 0; _i < value.length; _i++)if (isProcessableValue(value[_i])) string += processStyleName(_key) + ":" + processStyleValue(_key, value[_i]) + ";";
            } else {
                var interpolated = handleInterpolation(mergedProps, registered, value);
                switch(_key){
                    case "animation":
                    case "animationName":
                        string += processStyleName(_key) + ":" + interpolated + ";";
                        break;
                    default:
                        if (_key === "undefined") console.error(UNDEFINED_AS_OBJECT_KEY_ERROR);
                        string += _key + "{" + interpolated + "}";
                }
            }
        }
    }
    return string;
}
var labelPattern = /label:\s*([^\s;\n{]+)\s*(;|$)/g;
var sourceMapPattern;
sourceMapPattern = /\/\*#\ssourceMappingURL=data:application\/json;\S+\s+\*\//g;
// keyframes are stored on the SerializedStyles object as a linked list
var cursor;
var serializeStyles = function serializeStyles(args, registered, mergedProps) {
    if (args.length === 1 && typeof args[0] === "object" && args[0] !== null && args[0].styles !== undefined) return args[0];
    var stringMode = true;
    var styles = "";
    cursor = undefined;
    var strings = args[0];
    if (strings == null || strings.raw === undefined) {
        stringMode = false;
        styles += handleInterpolation(mergedProps, registered, strings);
    } else {
        if (strings[0] === undefined) console.error(ILLEGAL_ESCAPE_SEQUENCE_ERROR);
        styles += strings[0];
    } // we start at 1 since we've already handled the first arg
    for(var i = 1; i < args.length; i++){
        styles += handleInterpolation(mergedProps, registered, args[i]);
        if (stringMode) {
            if (strings[i] === undefined) console.error(ILLEGAL_ESCAPE_SEQUENCE_ERROR);
            styles += strings[i];
        }
    }
    var sourceMap;
    styles = styles.replace(sourceMapPattern, function(match) {
        sourceMap = match;
        return "";
    });
    labelPattern.lastIndex = 0;
    var identifierName = "";
    var match; // https://esbench.com/bench/5b809c2cf2949800a0f61fb5
    while((match = labelPattern.exec(styles)) !== null)identifierName += "-" + // $FlowFixMe we know it's not null
    match[1];
    var name = (0, _hashDefault.default)(styles) + identifierName;
    // $FlowFixMe SerializedStyles type doesn't have toString property (and we don't want to add it)
    return {
        name: name,
        styles: styles,
        map: sourceMap,
        next: cursor,
        toString: function toString() {
            return "You have tried to stringify object returned from `css` function. It isn't supposed to be used directly (e.g. as value of the `className` prop), but rather handed to emotion so it can handle it (e.g. as value of `css` prop).";
        }
    };
};

},{"@emotion/hash":"clggK","@emotion/unitless":"2Tu84","@emotion/memoize":"2vzJd","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"clggK":[function(require,module,exports) {
/* eslint-disable */ // Inspired by https://github.com/garycourt/murmurhash-js
// Ported from https://github.com/aappleby/smhasher/blob/61a0530f28277f2e850bfc39600ce61d02b518de/src/MurmurHash2.cpp#L37-L86
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>murmur2);
function murmur2(str) {
    // 'm' and 'r' are mixing constants generated offline.
    // They're not really 'magic', they just happen to work well.
    // const m = 0x5bd1e995;
    // const r = 24;
    // Initialize the hash
    var h = 0; // Mix 4 bytes at a time into the hash
    var k, i = 0, len = str.length;
    for(; len >= 4; ++i, len -= 4){
        k = str.charCodeAt(i) & 0xff | (str.charCodeAt(++i) & 0xff) << 8 | (str.charCodeAt(++i) & 0xff) << 16 | (str.charCodeAt(++i) & 0xff) << 24;
        k = /* Math.imul(k, m): */ (k & 0xffff) * 0x5bd1e995 + ((k >>> 16) * 0xe995 << 16);
        k ^= /* k >>> r: */ k >>> 24;
        h = /* Math.imul(k, m): */ (k & 0xffff) * 0x5bd1e995 + ((k >>> 16) * 0xe995 << 16) ^ /* Math.imul(h, m): */ (h & 0xffff) * 0x5bd1e995 + ((h >>> 16) * 0xe995 << 16);
    } // Handle the last few bytes of the input array
    switch(len){
        case 3:
            h ^= (str.charCodeAt(i + 2) & 0xff) << 16;
        case 2:
            h ^= (str.charCodeAt(i + 1) & 0xff) << 8;
        case 1:
            h ^= str.charCodeAt(i) & 0xff;
            h = /* Math.imul(h, m): */ (h & 0xffff) * 0x5bd1e995 + ((h >>> 16) * 0xe995 << 16);
    } // Do a few final mixes of the hash to ensure the last few
    // bytes are well-incorporated.
    h ^= h >>> 13;
    h = /* Math.imul(h, m): */ (h & 0xffff) * 0x5bd1e995 + ((h >>> 16) * 0xe995 << 16);
    return ((h ^ h >>> 15) >>> 0).toString(36);
}

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2Tu84":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "default", ()=>unitlessKeys);
var unitlessKeys = {
    animationIterationCount: 1,
    aspectRatio: 1,
    borderImageOutset: 1,
    borderImageSlice: 1,
    borderImageWidth: 1,
    boxFlex: 1,
    boxFlexGroup: 1,
    boxOrdinalGroup: 1,
    columnCount: 1,
    columns: 1,
    flex: 1,
    flexGrow: 1,
    flexPositive: 1,
    flexShrink: 1,
    flexNegative: 1,
    flexOrder: 1,
    gridRow: 1,
    gridRowEnd: 1,
    gridRowSpan: 1,
    gridRowStart: 1,
    gridColumn: 1,
    gridColumnEnd: 1,
    gridColumnSpan: 1,
    gridColumnStart: 1,
    msGridRow: 1,
    msGridRowSpan: 1,
    msGridColumn: 1,
    msGridColumnSpan: 1,
    fontWeight: 1,
    lineHeight: 1,
    opacity: 1,
    order: 1,
    orphans: 1,
    tabSize: 1,
    widows: 1,
    zIndex: 1,
    zoom: 1,
    WebkitLineClamp: 1,
    // SVG-related properties
    fillOpacity: 1,
    floodOpacity: 1,
    stopOpacity: 1,
    strokeDasharray: 1,
    strokeDashoffset: 1,
    strokeMiterlimit: 1,
    strokeOpacity: 1,
    strokeWidth: 1
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"6UI8e":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "getRegisteredStyles", ()=>getRegisteredStyles);
parcelHelpers.export(exports, "insertStyles", ()=>insertStyles);
parcelHelpers.export(exports, "registerStyles", ()=>registerStyles);
var isBrowser = true;
function getRegisteredStyles(registered, registeredStyles, classNames) {
    var rawClassName = "";
    classNames.split(" ").forEach(function(className) {
        if (registered[className] !== undefined) registeredStyles.push(registered[className] + ";");
        else rawClassName += className + " ";
    });
    return rawClassName;
}
var registerStyles = function registerStyles(cache, serialized, isStringTag) {
    var className = cache.key + "-" + serialized.name;
    if (// class name could be used further down
    // the tree but if it's a string tag, we know it won't
    // so we don't have to add it to registered cache.
    // this improves memory usage since we can avoid storing the whole style string
    (isStringTag === false || // we need to always store it if we're in compat mode and
    // in node since emotion-server relies on whether a style is in
    // the registered cache to know whether a style is global or not
    // also, note that this check will be dead code eliminated in the browser
    isBrowser === false) && cache.registered[className] === undefined) cache.registered[className] = serialized.styles;
};
var insertStyles = function insertStyles(cache, serialized, isStringTag) {
    registerStyles(cache, serialized, isStringTag);
    var className = cache.key + "-" + serialized.name;
    if (cache.inserted[serialized.name] === undefined) {
        var current = serialized;
        do {
            cache.insert(serialized === current ? "." + className : "", current, cache.sheet, true);
            current = current.next;
        }while (current !== undefined);
    }
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2D33e":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "aspectRatio", ()=>aspectRatio);
const aspectRatio = (ratio = "1/1")=>{
    return `
    aspect-ratio: ${ratio};
    @supports not (aspect-ratio: ${ratio}) {
        &::before {
            float: left;
            padding-top: 100% / ${ratio};
            content: "";
        }

        &::after {
            display: block;
            content: "";
            clear: both;
        }
    }
    `.trim();
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"celAt":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "bgColor", ()=>bgColor);
const Color = require("f6bcff9cde63c78a");
const bgColor = (color = "blue")=>{
    let fontColor = Color(color).isDark() ? "white" : "black";
    return `
    background-color: ${color};
    color: ${fontColor};
    `.trim();
};

},{"f6bcff9cde63c78a":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"gW2oi":[function(require,module,exports) {
const colorString = require("71b6e3b39cf59f9f");
const convert = require("c094f2fb379d5867");
const skippedModels = [
    // To be honest, I don't really feel like keyword belongs in color convert, but eh.
    "keyword",
    // Gray conflicts with some method names, and has its own method defined.
    "gray",
    // Shouldn't really be in color-convert either...
    "hex"
];
const hashedModelKeys = {};
for (const model of Object.keys(convert))hashedModelKeys[[
    ...convert[model].labels
].sort().join("")] = model;
const limiters = {};
function Color(object, model) {
    if (!(this instanceof Color)) return new Color(object, model);
    if (model && model in skippedModels) model = null;
    if (model && !(model in convert)) throw new Error("Unknown model: " + model);
    let i;
    let channels;
    if (object == null) {
        this.model = "rgb";
        this.color = [
            0,
            0,
            0
        ];
        this.valpha = 1;
    } else if (object instanceof Color) {
        this.model = object.model;
        this.color = [
            ...object.color
        ];
        this.valpha = object.valpha;
    } else if (typeof object === "string") {
        const result = colorString.get(object);
        if (result === null) throw new Error("Unable to parse color from string: " + object);
        this.model = result.model;
        channels = convert[this.model].channels;
        this.color = result.value.slice(0, channels);
        this.valpha = typeof result.value[channels] === "number" ? result.value[channels] : 1;
    } else if (object.length > 0) {
        this.model = model || "rgb";
        channels = convert[this.model].channels;
        const newArray = Array.prototype.slice.call(object, 0, channels);
        this.color = zeroArray(newArray, channels);
        this.valpha = typeof object[channels] === "number" ? object[channels] : 1;
    } else if (typeof object === "number") {
        // This is always RGB - can be converted later on.
        this.model = "rgb";
        this.color = [
            object >> 16 & 0xFF,
            object >> 8 & 0xFF,
            object & 0xFF
        ];
        this.valpha = 1;
    } else {
        this.valpha = 1;
        const keys = Object.keys(object);
        if ("alpha" in object) {
            keys.splice(keys.indexOf("alpha"), 1);
            this.valpha = typeof object.alpha === "number" ? object.alpha : 0;
        }
        const hashedKeys = keys.sort().join("");
        if (!(hashedKeys in hashedModelKeys)) throw new Error("Unable to parse color from object: " + JSON.stringify(object));
        this.model = hashedModelKeys[hashedKeys];
        const { labels } = convert[this.model];
        const color = [];
        for(i = 0; i < labels.length; i++)color.push(object[labels[i]]);
        this.color = zeroArray(color);
    }
    // Perform limitations (clamping, etc.)
    if (limiters[this.model]) {
        channels = convert[this.model].channels;
        for(i = 0; i < channels; i++){
            const limit = limiters[this.model][i];
            if (limit) this.color[i] = limit(this.color[i]);
        }
    }
    this.valpha = Math.max(0, Math.min(1, this.valpha));
    if (Object.freeze) Object.freeze(this);
}
Color.prototype = {
    toString () {
        return this.string();
    },
    toJSON () {
        return this[this.model]();
    },
    string (places) {
        let self = this.model in colorString.to ? this : this.rgb();
        self = self.round(typeof places === "number" ? places : 1);
        const args = self.valpha === 1 ? self.color : [
            ...self.color,
            this.valpha
        ];
        return colorString.to[self.model](args);
    },
    percentString (places) {
        const self = this.rgb().round(typeof places === "number" ? places : 1);
        const args = self.valpha === 1 ? self.color : [
            ...self.color,
            this.valpha
        ];
        return colorString.to.rgb.percent(args);
    },
    array () {
        return this.valpha === 1 ? [
            ...this.color
        ] : [
            ...this.color,
            this.valpha
        ];
    },
    object () {
        const result = {};
        const { channels } = convert[this.model];
        const { labels } = convert[this.model];
        for(let i = 0; i < channels; i++)result[labels[i]] = this.color[i];
        if (this.valpha !== 1) result.alpha = this.valpha;
        return result;
    },
    unitArray () {
        const rgb = this.rgb().color;
        rgb[0] /= 255;
        rgb[1] /= 255;
        rgb[2] /= 255;
        if (this.valpha !== 1) rgb.push(this.valpha);
        return rgb;
    },
    unitObject () {
        const rgb = this.rgb().object();
        rgb.r /= 255;
        rgb.g /= 255;
        rgb.b /= 255;
        if (this.valpha !== 1) rgb.alpha = this.valpha;
        return rgb;
    },
    round (places) {
        places = Math.max(places || 0, 0);
        return new Color([
            ...this.color.map(roundToPlace(places)),
            this.valpha
        ], this.model);
    },
    alpha (value) {
        if (value !== undefined) return new Color([
            ...this.color,
            Math.max(0, Math.min(1, value))
        ], this.model);
        return this.valpha;
    },
    // Rgb
    red: getset("rgb", 0, maxfn(255)),
    green: getset("rgb", 1, maxfn(255)),
    blue: getset("rgb", 2, maxfn(255)),
    hue: getset([
        "hsl",
        "hsv",
        "hsl",
        "hwb",
        "hcg"
    ], 0, (value)=>(value % 360 + 360) % 360),
    saturationl: getset("hsl", 1, maxfn(100)),
    lightness: getset("hsl", 2, maxfn(100)),
    saturationv: getset("hsv", 1, maxfn(100)),
    value: getset("hsv", 2, maxfn(100)),
    chroma: getset("hcg", 1, maxfn(100)),
    gray: getset("hcg", 2, maxfn(100)),
    white: getset("hwb", 1, maxfn(100)),
    wblack: getset("hwb", 2, maxfn(100)),
    cyan: getset("cmyk", 0, maxfn(100)),
    magenta: getset("cmyk", 1, maxfn(100)),
    yellow: getset("cmyk", 2, maxfn(100)),
    black: getset("cmyk", 3, maxfn(100)),
    x: getset("xyz", 0, maxfn(95.047)),
    y: getset("xyz", 1, maxfn(100)),
    z: getset("xyz", 2, maxfn(108.833)),
    l: getset("lab", 0, maxfn(100)),
    a: getset("lab", 1),
    b: getset("lab", 2),
    keyword (value) {
        if (value !== undefined) return new Color(value);
        return convert[this.model].keyword(this.color);
    },
    hex (value) {
        if (value !== undefined) return new Color(value);
        return colorString.to.hex(this.rgb().round().color);
    },
    hexa (value) {
        if (value !== undefined) return new Color(value);
        const rgbArray = this.rgb().round().color;
        let alphaHex = Math.round(this.valpha * 255).toString(16).toUpperCase();
        if (alphaHex.length === 1) alphaHex = "0" + alphaHex;
        return colorString.to.hex(rgbArray) + alphaHex;
    },
    rgbNumber () {
        const rgb = this.rgb().color;
        return (rgb[0] & 0xFF) << 16 | (rgb[1] & 0xFF) << 8 | rgb[2] & 0xFF;
    },
    luminosity () {
        // http://www.w3.org/TR/WCAG20/#relativeluminancedef
        const rgb = this.rgb().color;
        const lum = [];
        for (const [i, element] of rgb.entries()){
            const chan = element / 255;
            lum[i] = chan <= 0.04045 ? chan / 12.92 : ((chan + 0.055) / 1.055) ** 2.4;
        }
        return 0.2126 * lum[0] + 0.7152 * lum[1] + 0.0722 * lum[2];
    },
    contrast (color2) {
        // http://www.w3.org/TR/WCAG20/#contrast-ratiodef
        const lum1 = this.luminosity();
        const lum2 = color2.luminosity();
        if (lum1 > lum2) return (lum1 + 0.05) / (lum2 + 0.05);
        return (lum2 + 0.05) / (lum1 + 0.05);
    },
    level (color2) {
        // https://www.w3.org/TR/WCAG/#contrast-enhanced
        const contrastRatio = this.contrast(color2);
        if (contrastRatio >= 7) return "AAA";
        return contrastRatio >= 4.5 ? "AA" : "";
    },
    isDark () {
        // YIQ equation from http://24ways.org/2010/calculating-color-contrast
        const rgb = this.rgb().color;
        const yiq = (rgb[0] * 2126 + rgb[1] * 7152 + rgb[2] * 722) / 10000;
        return yiq < 128;
    },
    isLight () {
        return !this.isDark();
    },
    negate () {
        const rgb = this.rgb();
        for(let i = 0; i < 3; i++)rgb.color[i] = 255 - rgb.color[i];
        return rgb;
    },
    lighten (ratio) {
        const hsl = this.hsl();
        hsl.color[2] += hsl.color[2] * ratio;
        return hsl;
    },
    darken (ratio) {
        const hsl = this.hsl();
        hsl.color[2] -= hsl.color[2] * ratio;
        return hsl;
    },
    saturate (ratio) {
        const hsl = this.hsl();
        hsl.color[1] += hsl.color[1] * ratio;
        return hsl;
    },
    desaturate (ratio) {
        const hsl = this.hsl();
        hsl.color[1] -= hsl.color[1] * ratio;
        return hsl;
    },
    whiten (ratio) {
        const hwb = this.hwb();
        hwb.color[1] += hwb.color[1] * ratio;
        return hwb;
    },
    blacken (ratio) {
        const hwb = this.hwb();
        hwb.color[2] += hwb.color[2] * ratio;
        return hwb;
    },
    grayscale () {
        // http://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
        const rgb = this.rgb().color;
        const value = rgb[0] * 0.3 + rgb[1] * 0.59 + rgb[2] * 0.11;
        return Color.rgb(value, value, value);
    },
    fade (ratio) {
        return this.alpha(this.valpha - this.valpha * ratio);
    },
    opaquer (ratio) {
        return this.alpha(this.valpha + this.valpha * ratio);
    },
    rotate (degrees) {
        const hsl = this.hsl();
        let hue = hsl.color[0];
        hue = (hue + degrees) % 360;
        hue = hue < 0 ? 360 + hue : hue;
        hsl.color[0] = hue;
        return hsl;
    },
    mix (mixinColor, weight) {
        // Ported from sass implementation in C
        // https://github.com/sass/libsass/blob/0e6b4a2850092356aa3ece07c6b249f0221caced/functions.cpp#L209
        if (!mixinColor || !mixinColor.rgb) throw new Error('Argument to "mix" was not a Color instance, but rather an instance of ' + typeof mixinColor);
        const color1 = mixinColor.rgb();
        const color2 = this.rgb();
        const p = weight === undefined ? 0.5 : weight;
        const w = 2 * p - 1;
        const a = color1.alpha() - color2.alpha();
        const w1 = ((w * a === -1 ? w : (w + a) / (1 + w * a)) + 1) / 2;
        const w2 = 1 - w1;
        return Color.rgb(w1 * color1.red() + w2 * color2.red(), w1 * color1.green() + w2 * color2.green(), w1 * color1.blue() + w2 * color2.blue(), color1.alpha() * p + color2.alpha() * (1 - p));
    }
};
// Model conversion methods and static constructors
for (const model of Object.keys(convert)){
    if (skippedModels.includes(model)) continue;
    const { channels } = convert[model];
    // Conversion methods
    Color.prototype[model] = function(...args) {
        if (this.model === model) return new Color(this);
        if (args.length > 0) return new Color(args, model);
        return new Color([
            ...assertArray(convert[this.model][model].raw(this.color)),
            this.valpha
        ], model);
    };
    // 'static' construction methods
    Color[model] = function(...args) {
        let color = args[0];
        if (typeof color === "number") color = zeroArray(args, channels);
        return new Color(color, model);
    };
}
function roundTo(number, places) {
    return Number(number.toFixed(places));
}
function roundToPlace(places) {
    return function(number) {
        return roundTo(number, places);
    };
}
function getset(model, channel, modifier) {
    model = Array.isArray(model) ? model : [
        model
    ];
    for (const m of model)(limiters[m] || (limiters[m] = []))[channel] = modifier;
    model = model[0];
    return function(value) {
        let result;
        if (value !== undefined) {
            if (modifier) value = modifier(value);
            result = this[model]();
            result.color[channel] = value;
            return result;
        }
        result = this[model]().color[channel];
        if (modifier) result = modifier(result);
        return result;
    };
}
function maxfn(max) {
    return function(v) {
        return Math.max(0, Math.min(max, v));
    };
}
function assertArray(value) {
    return Array.isArray(value) ? value : [
        value
    ];
}
function zeroArray(array, length) {
    for(let i = 0; i < length; i++)if (typeof array[i] !== "number") array[i] = 0;
    return array;
}
module.exports = Color;

},{"71b6e3b39cf59f9f":"d9oJb","c094f2fb379d5867":"bvUlS"}],"d9oJb":[function(require,module,exports) {
/* MIT license */ var colorNames = require("d7a6eeb7388b4bb");
var swizzle = require("248ce9e419a8df53");
var hasOwnProperty = Object.hasOwnProperty;
var reverseNames = Object.create(null);
// create a list of reverse color names
for(var name in colorNames)if (hasOwnProperty.call(colorNames, name)) reverseNames[colorNames[name]] = name;
var cs = module.exports = {
    to: {},
    get: {}
};
cs.get = function(string) {
    var prefix = string.substring(0, 3).toLowerCase();
    var val;
    var model;
    switch(prefix){
        case "hsl":
            val = cs.get.hsl(string);
            model = "hsl";
            break;
        case "hwb":
            val = cs.get.hwb(string);
            model = "hwb";
            break;
        default:
            val = cs.get.rgb(string);
            model = "rgb";
            break;
    }
    if (!val) return null;
    return {
        model: model,
        value: val
    };
};
cs.get.rgb = function(string) {
    if (!string) return null;
    var abbr = /^#([a-f0-9]{3,4})$/i;
    var hex = /^#([a-f0-9]{6})([a-f0-9]{2})?$/i;
    var rgba = /^rgba?\(\s*([+-]?\d+)(?=[\s,])\s*(?:,\s*)?([+-]?\d+)(?=[\s,])\s*(?:,\s*)?([+-]?\d+)\s*(?:[,|\/]\s*([+-]?[\d\.]+)(%?)\s*)?\)$/;
    var per = /^rgba?\(\s*([+-]?[\d\.]+)\%\s*,?\s*([+-]?[\d\.]+)\%\s*,?\s*([+-]?[\d\.]+)\%\s*(?:[,|\/]\s*([+-]?[\d\.]+)(%?)\s*)?\)$/;
    var keyword = /^(\w+)$/;
    var rgb = [
        0,
        0,
        0,
        1
    ];
    var match;
    var i;
    var hexAlpha;
    if (match = string.match(hex)) {
        hexAlpha = match[2];
        match = match[1];
        for(i = 0; i < 3; i++){
            // https://jsperf.com/slice-vs-substr-vs-substring-methods-long-string/19
            var i2 = i * 2;
            rgb[i] = parseInt(match.slice(i2, i2 + 2), 16);
        }
        if (hexAlpha) rgb[3] = parseInt(hexAlpha, 16) / 255;
    } else if (match = string.match(abbr)) {
        match = match[1];
        hexAlpha = match[3];
        for(i = 0; i < 3; i++)rgb[i] = parseInt(match[i] + match[i], 16);
        if (hexAlpha) rgb[3] = parseInt(hexAlpha + hexAlpha, 16) / 255;
    } else if (match = string.match(rgba)) {
        for(i = 0; i < 3; i++)rgb[i] = parseInt(match[i + 1], 0);
        if (match[4]) {
            if (match[5]) rgb[3] = parseFloat(match[4]) * 0.01;
            else rgb[3] = parseFloat(match[4]);
        }
    } else if (match = string.match(per)) {
        for(i = 0; i < 3; i++)rgb[i] = Math.round(parseFloat(match[i + 1]) * 2.55);
        if (match[4]) {
            if (match[5]) rgb[3] = parseFloat(match[4]) * 0.01;
            else rgb[3] = parseFloat(match[4]);
        }
    } else if (match = string.match(keyword)) {
        if (match[1] === "transparent") return [
            0,
            0,
            0,
            0
        ];
        if (!hasOwnProperty.call(colorNames, match[1])) return null;
        rgb = colorNames[match[1]];
        rgb[3] = 1;
        return rgb;
    } else return null;
    for(i = 0; i < 3; i++)rgb[i] = clamp(rgb[i], 0, 255);
    rgb[3] = clamp(rgb[3], 0, 1);
    return rgb;
};
cs.get.hsl = function(string) {
    if (!string) return null;
    var hsl = /^hsla?\(\s*([+-]?(?:\d{0,3}\.)?\d+)(?:deg)?\s*,?\s*([+-]?[\d\.]+)%\s*,?\s*([+-]?[\d\.]+)%\s*(?:[,|\/]\s*([+-]?(?=\.\d|\d)(?:0|[1-9]\d*)?(?:\.\d*)?(?:[eE][+-]?\d+)?)\s*)?\)$/;
    var match = string.match(hsl);
    if (match) {
        var alpha = parseFloat(match[4]);
        var h = (parseFloat(match[1]) % 360 + 360) % 360;
        var s = clamp(parseFloat(match[2]), 0, 100);
        var l = clamp(parseFloat(match[3]), 0, 100);
        var a = clamp(isNaN(alpha) ? 1 : alpha, 0, 1);
        return [
            h,
            s,
            l,
            a
        ];
    }
    return null;
};
cs.get.hwb = function(string) {
    if (!string) return null;
    var hwb = /^hwb\(\s*([+-]?\d{0,3}(?:\.\d+)?)(?:deg)?\s*,\s*([+-]?[\d\.]+)%\s*,\s*([+-]?[\d\.]+)%\s*(?:,\s*([+-]?(?=\.\d|\d)(?:0|[1-9]\d*)?(?:\.\d*)?(?:[eE][+-]?\d+)?)\s*)?\)$/;
    var match = string.match(hwb);
    if (match) {
        var alpha = parseFloat(match[4]);
        var h = (parseFloat(match[1]) % 360 + 360) % 360;
        var w = clamp(parseFloat(match[2]), 0, 100);
        var b = clamp(parseFloat(match[3]), 0, 100);
        var a = clamp(isNaN(alpha) ? 1 : alpha, 0, 1);
        return [
            h,
            w,
            b,
            a
        ];
    }
    return null;
};
cs.to.hex = function() {
    var rgba = swizzle(arguments);
    return "#" + hexDouble(rgba[0]) + hexDouble(rgba[1]) + hexDouble(rgba[2]) + (rgba[3] < 1 ? hexDouble(Math.round(rgba[3] * 255)) : "");
};
cs.to.rgb = function() {
    var rgba = swizzle(arguments);
    return rgba.length < 4 || rgba[3] === 1 ? "rgb(" + Math.round(rgba[0]) + ", " + Math.round(rgba[1]) + ", " + Math.round(rgba[2]) + ")" : "rgba(" + Math.round(rgba[0]) + ", " + Math.round(rgba[1]) + ", " + Math.round(rgba[2]) + ", " + rgba[3] + ")";
};
cs.to.rgb.percent = function() {
    var rgba = swizzle(arguments);
    var r = Math.round(rgba[0] / 255 * 100);
    var g = Math.round(rgba[1] / 255 * 100);
    var b = Math.round(rgba[2] / 255 * 100);
    return rgba.length < 4 || rgba[3] === 1 ? "rgb(" + r + "%, " + g + "%, " + b + "%)" : "rgba(" + r + "%, " + g + "%, " + b + "%, " + rgba[3] + ")";
};
cs.to.hsl = function() {
    var hsla = swizzle(arguments);
    return hsla.length < 4 || hsla[3] === 1 ? "hsl(" + hsla[0] + ", " + hsla[1] + "%, " + hsla[2] + "%)" : "hsla(" + hsla[0] + ", " + hsla[1] + "%, " + hsla[2] + "%, " + hsla[3] + ")";
};
// hwb is a bit different than rgb(a) & hsl(a) since there is no alpha specific syntax
// (hwb have alpha optional & 1 is default value)
cs.to.hwb = function() {
    var hwba = swizzle(arguments);
    var a = "";
    if (hwba.length >= 4 && hwba[3] !== 1) a = ", " + hwba[3];
    return "hwb(" + hwba[0] + ", " + hwba[1] + "%, " + hwba[2] + "%" + a + ")";
};
cs.to.keyword = function(rgb) {
    return reverseNames[rgb.slice(0, 3)];
};
// helpers
function clamp(num, min, max) {
    return Math.min(Math.max(min, num), max);
}
function hexDouble(num) {
    var str = Math.round(num).toString(16).toUpperCase();
    return str.length < 2 ? "0" + str : str;
}

},{"d7a6eeb7388b4bb":"8NNt4","248ce9e419a8df53":"1jxJ4"}],"8NNt4":[function(require,module,exports) {
"use strict";
module.exports = {
    "aliceblue": [
        240,
        248,
        255
    ],
    "antiquewhite": [
        250,
        235,
        215
    ],
    "aqua": [
        0,
        255,
        255
    ],
    "aquamarine": [
        127,
        255,
        212
    ],
    "azure": [
        240,
        255,
        255
    ],
    "beige": [
        245,
        245,
        220
    ],
    "bisque": [
        255,
        228,
        196
    ],
    "black": [
        0,
        0,
        0
    ],
    "blanchedalmond": [
        255,
        235,
        205
    ],
    "blue": [
        0,
        0,
        255
    ],
    "blueviolet": [
        138,
        43,
        226
    ],
    "brown": [
        165,
        42,
        42
    ],
    "burlywood": [
        222,
        184,
        135
    ],
    "cadetblue": [
        95,
        158,
        160
    ],
    "chartreuse": [
        127,
        255,
        0
    ],
    "chocolate": [
        210,
        105,
        30
    ],
    "coral": [
        255,
        127,
        80
    ],
    "cornflowerblue": [
        100,
        149,
        237
    ],
    "cornsilk": [
        255,
        248,
        220
    ],
    "crimson": [
        220,
        20,
        60
    ],
    "cyan": [
        0,
        255,
        255
    ],
    "darkblue": [
        0,
        0,
        139
    ],
    "darkcyan": [
        0,
        139,
        139
    ],
    "darkgoldenrod": [
        184,
        134,
        11
    ],
    "darkgray": [
        169,
        169,
        169
    ],
    "darkgreen": [
        0,
        100,
        0
    ],
    "darkgrey": [
        169,
        169,
        169
    ],
    "darkkhaki": [
        189,
        183,
        107
    ],
    "darkmagenta": [
        139,
        0,
        139
    ],
    "darkolivegreen": [
        85,
        107,
        47
    ],
    "darkorange": [
        255,
        140,
        0
    ],
    "darkorchid": [
        153,
        50,
        204
    ],
    "darkred": [
        139,
        0,
        0
    ],
    "darksalmon": [
        233,
        150,
        122
    ],
    "darkseagreen": [
        143,
        188,
        143
    ],
    "darkslateblue": [
        72,
        61,
        139
    ],
    "darkslategray": [
        47,
        79,
        79
    ],
    "darkslategrey": [
        47,
        79,
        79
    ],
    "darkturquoise": [
        0,
        206,
        209
    ],
    "darkviolet": [
        148,
        0,
        211
    ],
    "deeppink": [
        255,
        20,
        147
    ],
    "deepskyblue": [
        0,
        191,
        255
    ],
    "dimgray": [
        105,
        105,
        105
    ],
    "dimgrey": [
        105,
        105,
        105
    ],
    "dodgerblue": [
        30,
        144,
        255
    ],
    "firebrick": [
        178,
        34,
        34
    ],
    "floralwhite": [
        255,
        250,
        240
    ],
    "forestgreen": [
        34,
        139,
        34
    ],
    "fuchsia": [
        255,
        0,
        255
    ],
    "gainsboro": [
        220,
        220,
        220
    ],
    "ghostwhite": [
        248,
        248,
        255
    ],
    "gold": [
        255,
        215,
        0
    ],
    "goldenrod": [
        218,
        165,
        32
    ],
    "gray": [
        128,
        128,
        128
    ],
    "green": [
        0,
        128,
        0
    ],
    "greenyellow": [
        173,
        255,
        47
    ],
    "grey": [
        128,
        128,
        128
    ],
    "honeydew": [
        240,
        255,
        240
    ],
    "hotpink": [
        255,
        105,
        180
    ],
    "indianred": [
        205,
        92,
        92
    ],
    "indigo": [
        75,
        0,
        130
    ],
    "ivory": [
        255,
        255,
        240
    ],
    "khaki": [
        240,
        230,
        140
    ],
    "lavender": [
        230,
        230,
        250
    ],
    "lavenderblush": [
        255,
        240,
        245
    ],
    "lawngreen": [
        124,
        252,
        0
    ],
    "lemonchiffon": [
        255,
        250,
        205
    ],
    "lightblue": [
        173,
        216,
        230
    ],
    "lightcoral": [
        240,
        128,
        128
    ],
    "lightcyan": [
        224,
        255,
        255
    ],
    "lightgoldenrodyellow": [
        250,
        250,
        210
    ],
    "lightgray": [
        211,
        211,
        211
    ],
    "lightgreen": [
        144,
        238,
        144
    ],
    "lightgrey": [
        211,
        211,
        211
    ],
    "lightpink": [
        255,
        182,
        193
    ],
    "lightsalmon": [
        255,
        160,
        122
    ],
    "lightseagreen": [
        32,
        178,
        170
    ],
    "lightskyblue": [
        135,
        206,
        250
    ],
    "lightslategray": [
        119,
        136,
        153
    ],
    "lightslategrey": [
        119,
        136,
        153
    ],
    "lightsteelblue": [
        176,
        196,
        222
    ],
    "lightyellow": [
        255,
        255,
        224
    ],
    "lime": [
        0,
        255,
        0
    ],
    "limegreen": [
        50,
        205,
        50
    ],
    "linen": [
        250,
        240,
        230
    ],
    "magenta": [
        255,
        0,
        255
    ],
    "maroon": [
        128,
        0,
        0
    ],
    "mediumaquamarine": [
        102,
        205,
        170
    ],
    "mediumblue": [
        0,
        0,
        205
    ],
    "mediumorchid": [
        186,
        85,
        211
    ],
    "mediumpurple": [
        147,
        112,
        219
    ],
    "mediumseagreen": [
        60,
        179,
        113
    ],
    "mediumslateblue": [
        123,
        104,
        238
    ],
    "mediumspringgreen": [
        0,
        250,
        154
    ],
    "mediumturquoise": [
        72,
        209,
        204
    ],
    "mediumvioletred": [
        199,
        21,
        133
    ],
    "midnightblue": [
        25,
        25,
        112
    ],
    "mintcream": [
        245,
        255,
        250
    ],
    "mistyrose": [
        255,
        228,
        225
    ],
    "moccasin": [
        255,
        228,
        181
    ],
    "navajowhite": [
        255,
        222,
        173
    ],
    "navy": [
        0,
        0,
        128
    ],
    "oldlace": [
        253,
        245,
        230
    ],
    "olive": [
        128,
        128,
        0
    ],
    "olivedrab": [
        107,
        142,
        35
    ],
    "orange": [
        255,
        165,
        0
    ],
    "orangered": [
        255,
        69,
        0
    ],
    "orchid": [
        218,
        112,
        214
    ],
    "palegoldenrod": [
        238,
        232,
        170
    ],
    "palegreen": [
        152,
        251,
        152
    ],
    "paleturquoise": [
        175,
        238,
        238
    ],
    "palevioletred": [
        219,
        112,
        147
    ],
    "papayawhip": [
        255,
        239,
        213
    ],
    "peachpuff": [
        255,
        218,
        185
    ],
    "peru": [
        205,
        133,
        63
    ],
    "pink": [
        255,
        192,
        203
    ],
    "plum": [
        221,
        160,
        221
    ],
    "powderblue": [
        176,
        224,
        230
    ],
    "purple": [
        128,
        0,
        128
    ],
    "rebeccapurple": [
        102,
        51,
        153
    ],
    "red": [
        255,
        0,
        0
    ],
    "rosybrown": [
        188,
        143,
        143
    ],
    "royalblue": [
        65,
        105,
        225
    ],
    "saddlebrown": [
        139,
        69,
        19
    ],
    "salmon": [
        250,
        128,
        114
    ],
    "sandybrown": [
        244,
        164,
        96
    ],
    "seagreen": [
        46,
        139,
        87
    ],
    "seashell": [
        255,
        245,
        238
    ],
    "sienna": [
        160,
        82,
        45
    ],
    "silver": [
        192,
        192,
        192
    ],
    "skyblue": [
        135,
        206,
        235
    ],
    "slateblue": [
        106,
        90,
        205
    ],
    "slategray": [
        112,
        128,
        144
    ],
    "slategrey": [
        112,
        128,
        144
    ],
    "snow": [
        255,
        250,
        250
    ],
    "springgreen": [
        0,
        255,
        127
    ],
    "steelblue": [
        70,
        130,
        180
    ],
    "tan": [
        210,
        180,
        140
    ],
    "teal": [
        0,
        128,
        128
    ],
    "thistle": [
        216,
        191,
        216
    ],
    "tomato": [
        255,
        99,
        71
    ],
    "turquoise": [
        64,
        224,
        208
    ],
    "violet": [
        238,
        130,
        238
    ],
    "wheat": [
        245,
        222,
        179
    ],
    "white": [
        255,
        255,
        255
    ],
    "whitesmoke": [
        245,
        245,
        245
    ],
    "yellow": [
        255,
        255,
        0
    ],
    "yellowgreen": [
        154,
        205,
        50
    ]
};

},{}],"1jxJ4":[function(require,module,exports) {
"use strict";
var isArrayish = require("ce0bf6d0bc000d24");
var concat = Array.prototype.concat;
var slice = Array.prototype.slice;
var swizzle = module.exports = function swizzle(args) {
    var results = [];
    for(var i = 0, len = args.length; i < len; i++){
        var arg = args[i];
        if (isArrayish(arg)) // http://jsperf.com/javascript-array-concat-vs-push/98
        results = concat.call(results, slice.call(arg));
        else results.push(arg);
    }
    return results;
};
swizzle.wrap = function(fn) {
    return function() {
        return fn(swizzle(arguments));
    };
};

},{"ce0bf6d0bc000d24":"ll30o"}],"ll30o":[function(require,module,exports) {
module.exports = function isArrayish(obj) {
    if (!obj || typeof obj === "string") return false;
    return obj instanceof Array || Array.isArray(obj) || obj.length >= 0 && (obj.splice instanceof Function || Object.getOwnPropertyDescriptor(obj, obj.length - 1) && obj.constructor.name !== "String");
};

},{}],"bvUlS":[function(require,module,exports) {
const conversions = require("739980f7990d3c32");
const route = require("30ea0c7ee5f3dd94");
const convert = {};
const models = Object.keys(conversions);
function wrapRaw(fn) {
    const wrappedFn = function(...args) {
        const arg0 = args[0];
        if (arg0 === undefined || arg0 === null) return arg0;
        if (arg0.length > 1) args = arg0;
        return fn(args);
    };
    // Preserve .conversion property if there is one
    if ("conversion" in fn) wrappedFn.conversion = fn.conversion;
    return wrappedFn;
}
function wrapRounded(fn) {
    const wrappedFn = function(...args) {
        const arg0 = args[0];
        if (arg0 === undefined || arg0 === null) return arg0;
        if (arg0.length > 1) args = arg0;
        const result = fn(args);
        // We're assuming the result is an array here.
        // see notice in conversions.js; don't use box types
        // in conversion functions.
        if (typeof result === "object") for(let len = result.length, i = 0; i < len; i++)result[i] = Math.round(result[i]);
        return result;
    };
    // Preserve .conversion property if there is one
    if ("conversion" in fn) wrappedFn.conversion = fn.conversion;
    return wrappedFn;
}
models.forEach((fromModel)=>{
    convert[fromModel] = {};
    Object.defineProperty(convert[fromModel], "channels", {
        value: conversions[fromModel].channels
    });
    Object.defineProperty(convert[fromModel], "labels", {
        value: conversions[fromModel].labels
    });
    const routes = route(fromModel);
    const routeModels = Object.keys(routes);
    routeModels.forEach((toModel)=>{
        const fn = routes[toModel];
        convert[fromModel][toModel] = wrapRounded(fn);
        convert[fromModel][toModel].raw = wrapRaw(fn);
    });
});
module.exports = convert;

},{"739980f7990d3c32":"C4O54","30ea0c7ee5f3dd94":"iJmBL"}],"C4O54":[function(require,module,exports) {
/* MIT license */ /* eslint-disable no-mixed-operators */ const cssKeywords = require("efc99055946c4df8");
// NOTE: conversions should only return primitive values (i.e. arrays, or
//       values that give correct `typeof` results).
//       do not use box values types (i.e. Number(), String(), etc.)
const reverseKeywords = {};
for (const key of Object.keys(cssKeywords))reverseKeywords[cssKeywords[key]] = key;
const convert = {
    rgb: {
        channels: 3,
        labels: "rgb"
    },
    hsl: {
        channels: 3,
        labels: "hsl"
    },
    hsv: {
        channels: 3,
        labels: "hsv"
    },
    hwb: {
        channels: 3,
        labels: "hwb"
    },
    cmyk: {
        channels: 4,
        labels: "cmyk"
    },
    xyz: {
        channels: 3,
        labels: "xyz"
    },
    lab: {
        channels: 3,
        labels: "lab"
    },
    lch: {
        channels: 3,
        labels: "lch"
    },
    hex: {
        channels: 1,
        labels: [
            "hex"
        ]
    },
    keyword: {
        channels: 1,
        labels: [
            "keyword"
        ]
    },
    ansi16: {
        channels: 1,
        labels: [
            "ansi16"
        ]
    },
    ansi256: {
        channels: 1,
        labels: [
            "ansi256"
        ]
    },
    hcg: {
        channels: 3,
        labels: [
            "h",
            "c",
            "g"
        ]
    },
    apple: {
        channels: 3,
        labels: [
            "r16",
            "g16",
            "b16"
        ]
    },
    gray: {
        channels: 1,
        labels: [
            "gray"
        ]
    }
};
module.exports = convert;
// Hide .channels and .labels properties
for (const model of Object.keys(convert)){
    if (!("channels" in convert[model])) throw new Error("missing channels property: " + model);
    if (!("labels" in convert[model])) throw new Error("missing channel labels property: " + model);
    if (convert[model].labels.length !== convert[model].channels) throw new Error("channel and label counts mismatch: " + model);
    const { channels, labels } = convert[model];
    delete convert[model].channels;
    delete convert[model].labels;
    Object.defineProperty(convert[model], "channels", {
        value: channels
    });
    Object.defineProperty(convert[model], "labels", {
        value: labels
    });
}
convert.rgb.hsl = function(rgb) {
    const r = rgb[0] / 255;
    const g = rgb[1] / 255;
    const b = rgb[2] / 255;
    const min = Math.min(r, g, b);
    const max = Math.max(r, g, b);
    const delta = max - min;
    let h;
    let s;
    if (max === min) h = 0;
    else if (r === max) h = (g - b) / delta;
    else if (g === max) h = 2 + (b - r) / delta;
    else if (b === max) h = 4 + (r - g) / delta;
    h = Math.min(h * 60, 360);
    if (h < 0) h += 360;
    const l = (min + max) / 2;
    if (max === min) s = 0;
    else if (l <= 0.5) s = delta / (max + min);
    else s = delta / (2 - max - min);
    return [
        h,
        s * 100,
        l * 100
    ];
};
convert.rgb.hsv = function(rgb) {
    let rdif;
    let gdif;
    let bdif;
    let h;
    let s;
    const r = rgb[0] / 255;
    const g = rgb[1] / 255;
    const b = rgb[2] / 255;
    const v = Math.max(r, g, b);
    const diff = v - Math.min(r, g, b);
    const diffc = function(c) {
        return (v - c) / 6 / diff + 0.5;
    };
    if (diff === 0) {
        h = 0;
        s = 0;
    } else {
        s = diff / v;
        rdif = diffc(r);
        gdif = diffc(g);
        bdif = diffc(b);
        if (r === v) h = bdif - gdif;
        else if (g === v) h = 1 / 3 + rdif - bdif;
        else if (b === v) h = 2 / 3 + gdif - rdif;
        if (h < 0) h += 1;
        else if (h > 1) h -= 1;
    }
    return [
        h * 360,
        s * 100,
        v * 100
    ];
};
convert.rgb.hwb = function(rgb) {
    const r = rgb[0];
    const g = rgb[1];
    let b = rgb[2];
    const h = convert.rgb.hsl(rgb)[0];
    const w = 1 / 255 * Math.min(r, Math.min(g, b));
    b = 1 - 1 / 255 * Math.max(r, Math.max(g, b));
    return [
        h,
        w * 100,
        b * 100
    ];
};
convert.rgb.cmyk = function(rgb) {
    const r = rgb[0] / 255;
    const g = rgb[1] / 255;
    const b = rgb[2] / 255;
    const k = Math.min(1 - r, 1 - g, 1 - b);
    const c = (1 - r - k) / (1 - k) || 0;
    const m = (1 - g - k) / (1 - k) || 0;
    const y = (1 - b - k) / (1 - k) || 0;
    return [
        c * 100,
        m * 100,
        y * 100,
        k * 100
    ];
};
function comparativeDistance(x, y) {
    /*
		See https://en.m.wikipedia.org/wiki/Euclidean_distance#Squared_Euclidean_distance
	*/ return (x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2 + (x[2] - y[2]) ** 2;
}
convert.rgb.keyword = function(rgb) {
    const reversed = reverseKeywords[rgb];
    if (reversed) return reversed;
    let currentClosestDistance = Infinity;
    let currentClosestKeyword;
    for (const keyword of Object.keys(cssKeywords)){
        const value = cssKeywords[keyword];
        // Compute comparative distance
        const distance = comparativeDistance(rgb, value);
        // Check if its less, if so set as closest
        if (distance < currentClosestDistance) {
            currentClosestDistance = distance;
            currentClosestKeyword = keyword;
        }
    }
    return currentClosestKeyword;
};
convert.keyword.rgb = function(keyword) {
    return cssKeywords[keyword];
};
convert.rgb.xyz = function(rgb) {
    let r = rgb[0] / 255;
    let g = rgb[1] / 255;
    let b = rgb[2] / 255;
    // Assume sRGB
    r = r > 0.04045 ? ((r + 0.055) / 1.055) ** 2.4 : r / 12.92;
    g = g > 0.04045 ? ((g + 0.055) / 1.055) ** 2.4 : g / 12.92;
    b = b > 0.04045 ? ((b + 0.055) / 1.055) ** 2.4 : b / 12.92;
    const x = r * 0.4124 + g * 0.3576 + b * 0.1805;
    const y = r * 0.2126 + g * 0.7152 + b * 0.0722;
    const z = r * 0.0193 + g * 0.1192 + b * 0.9505;
    return [
        x * 100,
        y * 100,
        z * 100
    ];
};
convert.rgb.lab = function(rgb) {
    const xyz = convert.rgb.xyz(rgb);
    let x = xyz[0];
    let y = xyz[1];
    let z = xyz[2];
    x /= 95.047;
    y /= 100;
    z /= 108.883;
    x = x > 0.008856 ? x ** (1 / 3) : 7.787 * x + 16 / 116;
    y = y > 0.008856 ? y ** (1 / 3) : 7.787 * y + 16 / 116;
    z = z > 0.008856 ? z ** (1 / 3) : 7.787 * z + 16 / 116;
    const l = 116 * y - 16;
    const a = 500 * (x - y);
    const b = 200 * (y - z);
    return [
        l,
        a,
        b
    ];
};
convert.hsl.rgb = function(hsl) {
    const h = hsl[0] / 360;
    const s = hsl[1] / 100;
    const l = hsl[2] / 100;
    let t2;
    let t3;
    let val;
    if (s === 0) {
        val = l * 255;
        return [
            val,
            val,
            val
        ];
    }
    if (l < 0.5) t2 = l * (1 + s);
    else t2 = l + s - l * s;
    const t1 = 2 * l - t2;
    const rgb = [
        0,
        0,
        0
    ];
    for(let i = 0; i < 3; i++){
        t3 = h + 1 / 3 * -(i - 1);
        if (t3 < 0) t3++;
        if (t3 > 1) t3--;
        if (6 * t3 < 1) val = t1 + (t2 - t1) * 6 * t3;
        else if (2 * t3 < 1) val = t2;
        else if (3 * t3 < 2) val = t1 + (t2 - t1) * (2 / 3 - t3) * 6;
        else val = t1;
        rgb[i] = val * 255;
    }
    return rgb;
};
convert.hsl.hsv = function(hsl) {
    const h = hsl[0];
    let s = hsl[1] / 100;
    let l = hsl[2] / 100;
    let smin = s;
    const lmin = Math.max(l, 0.01);
    l *= 2;
    s *= l <= 1 ? l : 2 - l;
    smin *= lmin <= 1 ? lmin : 2 - lmin;
    const v = (l + s) / 2;
    const sv = l === 0 ? 2 * smin / (lmin + smin) : 2 * s / (l + s);
    return [
        h,
        sv * 100,
        v * 100
    ];
};
convert.hsv.rgb = function(hsv) {
    const h = hsv[0] / 60;
    const s = hsv[1] / 100;
    let v = hsv[2] / 100;
    const hi = Math.floor(h) % 6;
    const f = h - Math.floor(h);
    const p = 255 * v * (1 - s);
    const q = 255 * v * (1 - s * f);
    const t = 255 * v * (1 - s * (1 - f));
    v *= 255;
    switch(hi){
        case 0:
            return [
                v,
                t,
                p
            ];
        case 1:
            return [
                q,
                v,
                p
            ];
        case 2:
            return [
                p,
                v,
                t
            ];
        case 3:
            return [
                p,
                q,
                v
            ];
        case 4:
            return [
                t,
                p,
                v
            ];
        case 5:
            return [
                v,
                p,
                q
            ];
    }
};
convert.hsv.hsl = function(hsv) {
    const h = hsv[0];
    const s = hsv[1] / 100;
    const v = hsv[2] / 100;
    const vmin = Math.max(v, 0.01);
    let sl;
    let l;
    l = (2 - s) * v;
    const lmin = (2 - s) * vmin;
    sl = s * vmin;
    sl /= lmin <= 1 ? lmin : 2 - lmin;
    sl = sl || 0;
    l /= 2;
    return [
        h,
        sl * 100,
        l * 100
    ];
};
// http://dev.w3.org/csswg/css-color/#hwb-to-rgb
convert.hwb.rgb = function(hwb) {
    const h = hwb[0] / 360;
    let wh = hwb[1] / 100;
    let bl = hwb[2] / 100;
    const ratio = wh + bl;
    let f;
    // Wh + bl cant be > 1
    if (ratio > 1) {
        wh /= ratio;
        bl /= ratio;
    }
    const i = Math.floor(6 * h);
    const v = 1 - bl;
    f = 6 * h - i;
    if ((i & 0x01) !== 0) f = 1 - f;
    const n = wh + f * (v - wh); // Linear interpolation
    let r;
    let g;
    let b;
    /* eslint-disable max-statements-per-line,no-multi-spaces */ switch(i){
        default:
        case 6:
        case 0:
            r = v;
            g = n;
            b = wh;
            break;
        case 1:
            r = n;
            g = v;
            b = wh;
            break;
        case 2:
            r = wh;
            g = v;
            b = n;
            break;
        case 3:
            r = wh;
            g = n;
            b = v;
            break;
        case 4:
            r = n;
            g = wh;
            b = v;
            break;
        case 5:
            r = v;
            g = wh;
            b = n;
            break;
    }
    /* eslint-enable max-statements-per-line,no-multi-spaces */ return [
        r * 255,
        g * 255,
        b * 255
    ];
};
convert.cmyk.rgb = function(cmyk) {
    const c = cmyk[0] / 100;
    const m = cmyk[1] / 100;
    const y = cmyk[2] / 100;
    const k = cmyk[3] / 100;
    const r = 1 - Math.min(1, c * (1 - k) + k);
    const g = 1 - Math.min(1, m * (1 - k) + k);
    const b = 1 - Math.min(1, y * (1 - k) + k);
    return [
        r * 255,
        g * 255,
        b * 255
    ];
};
convert.xyz.rgb = function(xyz) {
    const x = xyz[0] / 100;
    const y = xyz[1] / 100;
    const z = xyz[2] / 100;
    let r;
    let g;
    let b;
    r = x * 3.2406 + y * -1.5372 + z * -0.4986;
    g = x * -0.9689 + y * 1.8758 + z * 0.0415;
    b = x * 0.0557 + y * -0.204 + z * 1.0570;
    // Assume sRGB
    r = r > 0.0031308 ? 1.055 * r ** (1.0 / 2.4) - 0.055 : r * 12.92;
    g = g > 0.0031308 ? 1.055 * g ** (1.0 / 2.4) - 0.055 : g * 12.92;
    b = b > 0.0031308 ? 1.055 * b ** (1.0 / 2.4) - 0.055 : b * 12.92;
    r = Math.min(Math.max(0, r), 1);
    g = Math.min(Math.max(0, g), 1);
    b = Math.min(Math.max(0, b), 1);
    return [
        r * 255,
        g * 255,
        b * 255
    ];
};
convert.xyz.lab = function(xyz) {
    let x = xyz[0];
    let y = xyz[1];
    let z = xyz[2];
    x /= 95.047;
    y /= 100;
    z /= 108.883;
    x = x > 0.008856 ? x ** (1 / 3) : 7.787 * x + 16 / 116;
    y = y > 0.008856 ? y ** (1 / 3) : 7.787 * y + 16 / 116;
    z = z > 0.008856 ? z ** (1 / 3) : 7.787 * z + 16 / 116;
    const l = 116 * y - 16;
    const a = 500 * (x - y);
    const b = 200 * (y - z);
    return [
        l,
        a,
        b
    ];
};
convert.lab.xyz = function(lab) {
    const l = lab[0];
    const a = lab[1];
    const b = lab[2];
    let x;
    let y;
    let z;
    y = (l + 16) / 116;
    x = a / 500 + y;
    z = y - b / 200;
    const y2 = y ** 3;
    const x2 = x ** 3;
    const z2 = z ** 3;
    y = y2 > 0.008856 ? y2 : (y - 16 / 116) / 7.787;
    x = x2 > 0.008856 ? x2 : (x - 16 / 116) / 7.787;
    z = z2 > 0.008856 ? z2 : (z - 16 / 116) / 7.787;
    x *= 95.047;
    y *= 100;
    z *= 108.883;
    return [
        x,
        y,
        z
    ];
};
convert.lab.lch = function(lab) {
    const l = lab[0];
    const a = lab[1];
    const b = lab[2];
    let h;
    const hr = Math.atan2(b, a);
    h = hr * 360 / 2 / Math.PI;
    if (h < 0) h += 360;
    const c = Math.sqrt(a * a + b * b);
    return [
        l,
        c,
        h
    ];
};
convert.lch.lab = function(lch) {
    const l = lch[0];
    const c = lch[1];
    const h = lch[2];
    const hr = h / 360 * 2 * Math.PI;
    const a = c * Math.cos(hr);
    const b = c * Math.sin(hr);
    return [
        l,
        a,
        b
    ];
};
convert.rgb.ansi16 = function(args, saturation = null) {
    const [r, g, b] = args;
    let value = saturation === null ? convert.rgb.hsv(args)[2] : saturation; // Hsv -> ansi16 optimization
    value = Math.round(value / 50);
    if (value === 0) return 30;
    let ansi = 30 + (Math.round(b / 255) << 2 | Math.round(g / 255) << 1 | Math.round(r / 255));
    if (value === 2) ansi += 60;
    return ansi;
};
convert.hsv.ansi16 = function(args) {
    // Optimization here; we already know the value and don't need to get
    // it converted for us.
    return convert.rgb.ansi16(convert.hsv.rgb(args), args[2]);
};
convert.rgb.ansi256 = function(args) {
    const r = args[0];
    const g = args[1];
    const b = args[2];
    // We use the extended greyscale palette here, with the exception of
    // black and white. normal palette only has 4 greyscale shades.
    if (r === g && g === b) {
        if (r < 8) return 16;
        if (r > 248) return 231;
        return Math.round((r - 8) / 247 * 24) + 232;
    }
    const ansi = 16 + 36 * Math.round(r / 255 * 5) + 6 * Math.round(g / 255 * 5) + Math.round(b / 255 * 5);
    return ansi;
};
convert.ansi16.rgb = function(args) {
    let color = args % 10;
    // Handle greyscale
    if (color === 0 || color === 7) {
        if (args > 50) color += 3.5;
        color = color / 10.5 * 255;
        return [
            color,
            color,
            color
        ];
    }
    const mult = (~~(args > 50) + 1) * 0.5;
    const r = (color & 1) * mult * 255;
    const g = (color >> 1 & 1) * mult * 255;
    const b = (color >> 2 & 1) * mult * 255;
    return [
        r,
        g,
        b
    ];
};
convert.ansi256.rgb = function(args) {
    // Handle greyscale
    if (args >= 232) {
        const c = (args - 232) * 10 + 8;
        return [
            c,
            c,
            c
        ];
    }
    args -= 16;
    let rem;
    const r = Math.floor(args / 36) / 5 * 255;
    const g = Math.floor((rem = args % 36) / 6) / 5 * 255;
    const b = rem % 6 / 5 * 255;
    return [
        r,
        g,
        b
    ];
};
convert.rgb.hex = function(args) {
    const integer = ((Math.round(args[0]) & 0xFF) << 16) + ((Math.round(args[1]) & 0xFF) << 8) + (Math.round(args[2]) & 0xFF);
    const string = integer.toString(16).toUpperCase();
    return "000000".substring(string.length) + string;
};
convert.hex.rgb = function(args) {
    const match = args.toString(16).match(/[a-f0-9]{6}|[a-f0-9]{3}/i);
    if (!match) return [
        0,
        0,
        0
    ];
    let colorString = match[0];
    if (match[0].length === 3) colorString = colorString.split("").map((char)=>{
        return char + char;
    }).join("");
    const integer = parseInt(colorString, 16);
    const r = integer >> 16 & 0xFF;
    const g = integer >> 8 & 0xFF;
    const b = integer & 0xFF;
    return [
        r,
        g,
        b
    ];
};
convert.rgb.hcg = function(rgb) {
    const r = rgb[0] / 255;
    const g = rgb[1] / 255;
    const b = rgb[2] / 255;
    const max = Math.max(Math.max(r, g), b);
    const min = Math.min(Math.min(r, g), b);
    const chroma = max - min;
    let grayscale;
    let hue;
    if (chroma < 1) grayscale = min / (1 - chroma);
    else grayscale = 0;
    if (chroma <= 0) hue = 0;
    else if (max === r) hue = (g - b) / chroma % 6;
    else if (max === g) hue = 2 + (b - r) / chroma;
    else hue = 4 + (r - g) / chroma;
    hue /= 6;
    hue %= 1;
    return [
        hue * 360,
        chroma * 100,
        grayscale * 100
    ];
};
convert.hsl.hcg = function(hsl) {
    const s = hsl[1] / 100;
    const l = hsl[2] / 100;
    const c = l < 0.5 ? 2.0 * s * l : 2.0 * s * (1.0 - l);
    let f = 0;
    if (c < 1.0) f = (l - 0.5 * c) / (1.0 - c);
    return [
        hsl[0],
        c * 100,
        f * 100
    ];
};
convert.hsv.hcg = function(hsv) {
    const s = hsv[1] / 100;
    const v = hsv[2] / 100;
    const c = s * v;
    let f = 0;
    if (c < 1.0) f = (v - c) / (1 - c);
    return [
        hsv[0],
        c * 100,
        f * 100
    ];
};
convert.hcg.rgb = function(hcg) {
    const h = hcg[0] / 360;
    const c = hcg[1] / 100;
    const g = hcg[2] / 100;
    if (c === 0.0) return [
        g * 255,
        g * 255,
        g * 255
    ];
    const pure = [
        0,
        0,
        0
    ];
    const hi = h % 1 * 6;
    const v = hi % 1;
    const w = 1 - v;
    let mg = 0;
    /* eslint-disable max-statements-per-line */ switch(Math.floor(hi)){
        case 0:
            pure[0] = 1;
            pure[1] = v;
            pure[2] = 0;
            break;
        case 1:
            pure[0] = w;
            pure[1] = 1;
            pure[2] = 0;
            break;
        case 2:
            pure[0] = 0;
            pure[1] = 1;
            pure[2] = v;
            break;
        case 3:
            pure[0] = 0;
            pure[1] = w;
            pure[2] = 1;
            break;
        case 4:
            pure[0] = v;
            pure[1] = 0;
            pure[2] = 1;
            break;
        default:
            pure[0] = 1;
            pure[1] = 0;
            pure[2] = w;
    }
    /* eslint-enable max-statements-per-line */ mg = (1.0 - c) * g;
    return [
        (c * pure[0] + mg) * 255,
        (c * pure[1] + mg) * 255,
        (c * pure[2] + mg) * 255
    ];
};
convert.hcg.hsv = function(hcg) {
    const c = hcg[1] / 100;
    const g = hcg[2] / 100;
    const v = c + g * (1.0 - c);
    let f = 0;
    if (v > 0.0) f = c / v;
    return [
        hcg[0],
        f * 100,
        v * 100
    ];
};
convert.hcg.hsl = function(hcg) {
    const c = hcg[1] / 100;
    const g = hcg[2] / 100;
    const l = g * (1.0 - c) + 0.5 * c;
    let s = 0;
    if (l > 0.0 && l < 0.5) s = c / (2 * l);
    else if (l >= 0.5 && l < 1.0) s = c / (2 * (1 - l));
    return [
        hcg[0],
        s * 100,
        l * 100
    ];
};
convert.hcg.hwb = function(hcg) {
    const c = hcg[1] / 100;
    const g = hcg[2] / 100;
    const v = c + g * (1.0 - c);
    return [
        hcg[0],
        (v - c) * 100,
        (1 - v) * 100
    ];
};
convert.hwb.hcg = function(hwb) {
    const w = hwb[1] / 100;
    const b = hwb[2] / 100;
    const v = 1 - b;
    const c = v - w;
    let g = 0;
    if (c < 1) g = (v - c) / (1 - c);
    return [
        hwb[0],
        c * 100,
        g * 100
    ];
};
convert.apple.rgb = function(apple) {
    return [
        apple[0] / 65535 * 255,
        apple[1] / 65535 * 255,
        apple[2] / 65535 * 255
    ];
};
convert.rgb.apple = function(rgb) {
    return [
        rgb[0] / 255 * 65535,
        rgb[1] / 255 * 65535,
        rgb[2] / 255 * 65535
    ];
};
convert.gray.rgb = function(args) {
    return [
        args[0] / 100 * 255,
        args[0] / 100 * 255,
        args[0] / 100 * 255
    ];
};
convert.gray.hsl = function(args) {
    return [
        0,
        0,
        args[0]
    ];
};
convert.gray.hsv = convert.gray.hsl;
convert.gray.hwb = function(gray) {
    return [
        0,
        100,
        gray[0]
    ];
};
convert.gray.cmyk = function(gray) {
    return [
        0,
        0,
        0,
        gray[0]
    ];
};
convert.gray.lab = function(gray) {
    return [
        gray[0],
        0,
        0
    ];
};
convert.gray.hex = function(gray) {
    const val = Math.round(gray[0] / 100 * 255) & 0xFF;
    const integer = (val << 16) + (val << 8) + val;
    const string = integer.toString(16).toUpperCase();
    return "000000".substring(string.length) + string;
};
convert.rgb.gray = function(rgb) {
    const val = (rgb[0] + rgb[1] + rgb[2]) / 3;
    return [
        val / 255 * 100
    ];
};

},{"efc99055946c4df8":"8NNt4"}],"iJmBL":[function(require,module,exports) {
const conversions = require("22442592002c5ac3");
/*
	This function routes a model to all other models.

	all functions that are routed have a property `.conversion` attached
	to the returned synthetic function. This property is an array
	of strings, each with the steps in between the 'from' and 'to'
	color models (inclusive).

	conversions that are not possible simply are not included.
*/ function buildGraph() {
    const graph = {};
    // https://jsperf.com/object-keys-vs-for-in-with-closure/3
    const models = Object.keys(conversions);
    for(let len = models.length, i = 0; i < len; i++)graph[models[i]] = {
        // http://jsperf.com/1-vs-infinity
        // micro-opt, but this is simple.
        distance: -1,
        parent: null
    };
    return graph;
}
// https://en.wikipedia.org/wiki/Breadth-first_search
function deriveBFS(fromModel) {
    const graph = buildGraph();
    const queue = [
        fromModel
    ]; // Unshift -> queue -> pop
    graph[fromModel].distance = 0;
    while(queue.length){
        const current = queue.pop();
        const adjacents = Object.keys(conversions[current]);
        for(let len = adjacents.length, i = 0; i < len; i++){
            const adjacent = adjacents[i];
            const node = graph[adjacent];
            if (node.distance === -1) {
                node.distance = graph[current].distance + 1;
                node.parent = current;
                queue.unshift(adjacent);
            }
        }
    }
    return graph;
}
function link(from, to) {
    return function(args) {
        return to(from(args));
    };
}
function wrapConversion(toModel, graph) {
    const path = [
        graph[toModel].parent,
        toModel
    ];
    let fn = conversions[graph[toModel].parent][toModel];
    let cur = graph[toModel].parent;
    while(graph[cur].parent){
        path.unshift(graph[cur].parent);
        fn = link(conversions[graph[cur].parent][cur], fn);
        cur = graph[cur].parent;
    }
    fn.conversion = path;
    return fn;
}
module.exports = function(fromModel) {
    const graph = deriveBFS(fromModel);
    const conversion = {};
    const models = Object.keys(graph);
    for(let len = models.length, i = 0; i < len; i++){
        const toModel = models[i];
        const node = graph[toModel];
        if (node.parent === null) continue;
        conversion[toModel] = wrapConversion(toModel, graph);
    }
    return conversion;
};

},{"22442592002c5ac3":"C4O54"}],"ckzzz":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "bgColorInt", ()=>bgColorInt);
var _color = require("color");
var _colorDefault = parcelHelpers.interopDefault(_color);
var _bgColor = require("./bg-color");
const bgColorInt = ({ color = "blue", lighten = 0.2, saturate = 0.2 })=>{
    const color_ = new (0, _colorDefault.default)(color);
    const hoverColor = color_.lighten(lighten).saturate(saturate);
    return `
    ${(0, _bgColor.bgColor)(color_.toString())}
    &:hover {
        background-color: ${color_.lighten(lighten).saturate(saturate).toString()};
    }
    &:active {
        background-color: ${color_.lighten(-lighten).saturate(saturate).toString()};
    }`.trim();
};

},{"color":"gW2oi","./bg-color":"celAt","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"g8Grc":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "fontFluid", ()=>fontFluid);
const fontFluid = ({ vwMin = 300, vwMax = 1200, fontSizeMin = 16, fontSizeMax = 18 } = {})=>{
    let viewportRatio = `(100vw - ${vwMin}px) / (${vwMax} - ${vwMin})`;
    let fontScaleRatio = `(${fontSizeMax} - ${fontSizeMin}) * ${viewportRatio}`;
    return `
    font-size: ${fontSizeMin}px;
    @media screen and (min-width: ${vwMin}px) {
        font-size: calc(
            ${fontSizeMin}px + ${fontScaleRatio}
        );
    }
    @media screen and (min-width: ${vwMax}px) {
        font-size: ${fontSizeMax}px;
    }
    `.trim();
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9caa5":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "lift", ()=>lift);
const lift = ({ level = 3, shadowColor = "rgb(0, 0, 0, 50%)" })=>{
    if (level < 0 || level > 5) level = 0;
    const boxShadow = [
        `0 0 0 0 ${shadowColor}`,
        `0 1px 3px 0 ${shadowColor}`,
        `0 2px 5px 0 ${shadowColor}`,
        `0 4px 9px 0 ${shadowColor}`,
        `0 8px 17px 0 ${shadowColor}`,
        `0 16px 33px 0 ${shadowColor}`
    ];
    return `box-shadow: ${boxShadow[level]};`.trim();
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"hRUly":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Badge", ()=>Badge);
var _adapter = require("@nitipit/adapter/src/adapter");
var _badgeStyle = require("./badge.style");
class Badge extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _badgeStyle.BadgeStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./badge.style":"jMFLV","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"jMFLV":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "BadgeStyle", ()=>BadgeStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class BadgeStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        return `
        display: inline-flex;
        justify-content: center;
        align-items: center;
        font-size: 1em;
        line-height: initial;
        border-radius: 20em;
        padding-left: 0.2em;
        padding-right: 0.2em;
        min-width: 1.5em;
        min-height: 1.7em;
        ${this.style(style)}
        `.trim();
    }
    static style(style = {}) {
        let css = `
        ${this._color(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return (0, _style.bgColor)(style.color);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"lPBya":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "BoxArrow", ()=>BoxArrow);
var _adapter = require("@nitipit/adapter/src/adapter");
var _boxArrowStyle = require("./box-arrow.style");
var _uhtml = require("uhtml");
class BoxArrow extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _boxArrowStyle.BoxArrowStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this._innerHTML = this.innerHTML;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
        <div el="box"></div>
        <div el="arrows">
            <div el="arrow-top"></div>
            <div el="arrow-right"></div>
            <div el="arrow-bottom"></div>
            <div el="arrow-left"></div>
        </div>
        `);
        const box = this.querySelector('[el="box"]');
        box.innerHTML = this._innerHTML;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./box-arrow.style":"9cqGe","uhtml":"if09d","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9cqGe":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "BoxArrowStyle", ()=>BoxArrowStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class BoxArrowStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            arrow: "top",
            arrowSize: "8px",
            position: "50%",
            bgColor: "#ccc",
            borderWidth: "1px",
            borderStyle: "solid",
            borderColor: "black",
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        display: inline-block;
        position: relative;

        div[el="box"] {
            position: relative;
            background: inherit;
            z-index: 1;
        }

        div[el="arrows"] {
            background: inherit;
        }

        div[el="arrow-top"] {
            position: absolute;
            top: 0;
            background: inherit;
            transform: translate(-50%, -50%) rotate(45deg);
        }

        div[el="arrow-right"] {
            position: absolute;
            right: 0;
            background: inherit;
            transform: translate(50%, -50%) rotate(135deg);
        }

        div[el="arrow-bottom"] {
            position: absolute;
            bottom: 0;
            background: inherit;
            transform: translate(50%, 50%) rotate(225deg);
        }

        div[el="arrow-left"] {
            position: absolute;
            left: 0;
            background: inherit;
            transform: translate(-50%, 50%) rotate(315deg);
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._arrow(style)}
        ${this._arrowSize(style)}
        ${this._position(style)}
        ${this._bgColor(style)}
        ${this._borderWidth(style)}
        ${this._borderStyle(style)}
        ${this._borderColor(style)}
        ${this._borderRadius(style)}

        `.trim();
        return css;
    }
    static _arrow(style = {}) {
        if (style.arrow == undefined) return "";
        let css = `
        div[el^="arrow-"] {
            display: none;
        }
        div[el="arrow-${style.arrow}"] {
            display: block;
        }
        `.trim();
        return css;
    }
    static _arrowSize(style = {}) {
        if (style.arrowSize == undefined) return "";
        let css = `
        div[el^="arrow-"] {
            width: ${style.arrowSize};
            height: ${style.arrowSize};
        }
        `.trim();
        return css;
    }
    static _position(style = {}) {
        if (style.position == undefined) return "";
        let css = `
        div[el="arrow-top"] {
            left: ${style.position};
        }
        div[el="arrow-right"] {
            top: ${style.position};
        }
        div[el="arrow-bottom"] {
            right: ${style.position};
        }
        div[el="arrow-left"] {
            bottom: ${style.position};
        }
        `.trim();
        return css;
    }
    static _bgColor(style = {}) {
        if (style.bgColor == undefined) return "";
        let css = `
        ${(0, _style.bgColor)(style.bgColor)}
        `.trim();
        return css;
    }
    static _borderWidth(style = {}) {
        if (style.borderWidth == undefined) return "";
        let css = `
        border-width: ${style.borderWidth};
        div[el^="arrow-"] {
            border-width: ${style.borderWidth}
        }
        `.trim();
        return css;
    }
    static _borderStyle(style = {}) {
        if (style.borderStyle == undefined) return "";
        let css = `
        border-style: ${style.borderStyle};
        div[el^="arrow-"] {
            border-style: ${style.borderStyle}
        }
        `.trim();
        return css;
    }
    static _borderColor(style = {}) {
        if (style.borderColor == undefined) return "";
        let css = `
        border-color: ${style.borderColor};
        div[el^="arrow-"] {
            border-color: ${style.borderColor};
            border-bottom-color: transparent;
            border-right-color: transparent;
        }
        `.trim();
        return css;
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        let css = `
        border-radius: ${style.borderRadius};
        div[el="box"] {
            border-radius: ${style.borderRadius};
        }
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"if09d":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Hole", ()=>(0, _rabbitJs.Hole));
parcelHelpers.export(exports, "render", ()=>render);
parcelHelpers.export(exports, "html", ()=>html);
parcelHelpers.export(exports, "svg", ()=>svg);
parcelHelpers.export(exports, "foreign", ()=>(0, _uhandlers.foreign));
var _umap = require("umap");
var _umapDefault = parcelHelpers.interopDefault(_umap);
var _rabbitJs = require("./rabbit.js");
var _uhandlers = require("uhandlers");
const { create, defineProperties } = Object;
// both `html` and `svg` template literal tags are polluted
// with a `for(ref[, id])` and a `node` tag too
const tag = (type)=>{
    // both `html` and `svg` tags have their own cache
    const keyed = (0, _umapDefault.default)(new WeakMap);
    // keyed operations always re-use the same cache and unroll
    // the template and its interpolations right away
    const fixed = (cache)=>(template, ...values)=>(0, _rabbitJs.unroll)(cache, {
                type,
                template,
                values
            });
    return defineProperties(// non keyed operations are recognized as instance of Hole
    // during the "unroll", recursively resolved and updated
    (template, ...values)=>new (0, _rabbitJs.Hole)(type, template, values), {
        for: {
            // keyed operations need a reference object, usually the parent node
            // which is showing keyed results, and optionally a unique id per each
            // related node, handy with JSON results and mutable list of objects
            // that usually carry a unique identifier
            value (ref, id) {
                const memo = keyed.get(ref) || keyed.set(ref, create(null));
                return memo[id] || (memo[id] = fixed((0, _rabbitJs.createCache)()));
            }
        },
        node: {
            // it is possible to create one-off content out of the box via node tag
            // this might return the single created node, or a fragment with all
            // nodes present at the root level and, of course, their child nodes
            value: (template, ...values)=>(0, _rabbitJs.unroll)((0, _rabbitJs.createCache)(), {
                    type,
                    template,
                    values
                }).valueOf()
        }
    });
};
// each rendered node gets its own cache
const cache = (0, _umapDefault.default)(new WeakMap);
// rendering means understanding what `html` or `svg` tags returned
// and it relates a specific node to its own unique cache.
// Each time the content to render changes, the node is cleaned up
// and the new new content is appended, and if such content is a Hole
// then it's "unrolled" to resolve all its inner nodes.
const render = (where, what)=>{
    const hole = typeof what === "function" ? what() : what;
    const info = cache.get(where) || cache.set(where, (0, _rabbitJs.createCache)());
    const wire = hole instanceof (0, _rabbitJs.Hole) ? (0, _rabbitJs.unroll)(info, hole) : hole;
    if (wire !== info.wire) {
        info.wire = wire;
        where.textContent = "";
        // valueOf() simply returns the node itself, but in case it was a "wire"
        // it will eventually re-append all nodes to its fragment so that such
        // fragment can be re-appended many times in a meaningful way
        // (wires are basically persistent fragments facades with special behavior)
        where.appendChild(wire.valueOf());
    }
    return where;
};
const html = tag("html");
const svg = tag("svg");

},{"umap":"b3ep2","./rabbit.js":"4YYgA","uhandlers":"ceEOD","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"b3ep2":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
exports.default = (_)=>({
        // About: get: _.get.bind(_)
        // It looks like WebKit/Safari didn't optimize bind at all,
        // so that using bind slows it down by 60%.
        // Firefox and Chrome are just fine in both cases,
        // so let's use the approach that works fast everywhere 👍
        get: (key)=>_.get(key),
        set: (key, value)=>(_.set(key, value), value)
    });

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"4YYgA":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "createCache", ()=>createCache);
parcelHelpers.export(exports, "unroll", ()=>unroll);
/**
 * Holds all details wrappers needed to render the content further on.
 * @constructor
 * @param {string} type The hole type, either `html` or `svg`.
 * @param {string[]} template The template literals used to the define the content.
 * @param {Array} values Zero, one, or more interpolated values to render.
 */ parcelHelpers.export(exports, "Hole", ()=>Hole);
var _umap = require("umap");
var _umapDefault = parcelHelpers.interopDefault(_umap);
var _uparser = require("uparser");
var _uparserDefault = parcelHelpers.interopDefault(_uparser);
var _uarray = require("uarray");
var _uwire = require("uwire");
var _handlersJs = require("./handlers.js");
var _nodeJs = require("./node.js");
// from a fragment container, create an array of indexes
// related to its child nodes, so that it's possible
// to retrieve later on exact node via reducePath
const createPath = (node)=>{
    const path = [];
    let { parentNode } = node;
    while(parentNode){
        path.push((0, _uarray.indexOf).call(parentNode.childNodes, node));
        node = parentNode;
        parentNode = node.parentNode;
    }
    return path;
};
// the prefix is used to identify either comments, attributes, or nodes
// that contain the related unique id. In the attribute cases
// isµX="attribute-name" will be used to map current X update to that
// attribute name, while comments will be like <!--isµX-->, to map
// the update to that specific comment node, hence its parent.
// style and textarea will have <!--isµX--> text content, and are handled
// directly through text-only updates.
const prefix = "is\xb5";
// Template Literals are unique per scope and static, meaning a template
// should be parsed once, and once only, as it will always represent the same
// content, within the exact same amount of updates each time.
// This cache relates each template to its unique content and updates.
const cache = (0, _umapDefault.default)(new WeakMap);
// a RegExp that helps checking nodes that cannot contain comments
const textOnly = /^(?:plaintext|script|style|textarea|title|xmp)$/i;
const createCache = ()=>({
        stack: [],
        entry: null,
        //  * the template that is representing
        //  * the type of node it represents (html or svg)
        //  * the content fragment with all nodes
        //  * the list of updates per each node (template holes)
        //  * the "wired" node or fragment that will get updates
        // if the template or type are different from the previous one
        // the entry gets re-created each time
        wire: null // each rendered node represent some wired content and
    });
// the entry stored in the rendered node cache, and per each "hole"
const createEntry = (type, template)=>{
    const { content, updates } = mapUpdates(type, template);
    return {
        type,
        template,
        content,
        updates,
        wire: null
    };
};
// a template is instrumented to be able to retrieve where updates are needed.
// Each unique template becomes a fragment, cloned once per each other
// operation based on the same template, i.e. data => html`<p>${data}</p>`
const mapTemplate = (type, template)=>{
    const text = (0, _uparserDefault.default)(template, prefix, type === "svg");
    const content = (0, _nodeJs.createFragment)(text, type);
    // once instrumented and reproduced as fragment, it's crawled
    // to find out where each update is in the fragment tree
    const tw = (0, _nodeJs.createWalker)(content);
    const nodes = [];
    const length = template.length - 1;
    let i = 0;
    // updates are searched via unique names, linearly increased across the tree
    // <div isµ0="attr" isµ1="other"><!--isµ2--><style><!--isµ3--</style></div>
    let search = `${prefix}${i}`;
    while(i < length){
        const node = tw.nextNode();
        // if not all updates are bound but there's nothing else to crawl
        // it means that there is something wrong with the template.
        if (!node) throw `bad template: ${text}`;
        // if the current node is a comment, and it contains isµX
        // it means the update should take care of any content
        if (node.nodeType === 8) // The only comments to be considered are those
        // which content is exactly the same as the searched one.
        {
            if (node.data === search) {
                nodes.push({
                    type: "node",
                    path: createPath(node)
                });
                search = `${prefix}${++i}`;
            }
        } else {
            // if the node is not a comment, loop through all its attributes
            // named isµX and relate attribute updates to this node and the
            // attribute name, retrieved through node.getAttribute("isµX")
            // the isµX attribute will be removed as irrelevant for the layout
            // let svg = -1;
            while(node.hasAttribute(search)){
                nodes.push({
                    type: "attr",
                    path: createPath(node),
                    name: node.getAttribute(search)
                });
                node.removeAttribute(search);
                search = `${prefix}${++i}`;
            }
            // if the node was a style, textarea, or others, check its content
            // and if it is <!--isµX--> then update tex-only this node
            if (textOnly.test(node.tagName) && node.textContent.trim() === `<!--${search}-->`) {
                node.textContent = "";
                nodes.push({
                    type: "text",
                    path: createPath(node)
                });
                search = `${prefix}${++i}`;
            }
        }
    }
    // once all nodes to update, or their attributes, are known, the content
    // will be cloned in the future to represent the template, and all updates
    // related to such content retrieved right away without needing to re-crawl
    // the exact same template, and its content, more than once.
    return {
        content,
        nodes
    };
};
// if a template is unknown, perform the previous mapping, otherwise grab
// its details such as the fragment with all nodes, and updates info.
const mapUpdates = (type, template)=>{
    const { content, nodes } = cache.get(template) || cache.set(template, mapTemplate(type, template));
    // clone deeply the fragment
    const fragment = document.importNode(content, true);
    // and relate an update handler per each node that needs one
    const updates = nodes.map((0, _handlersJs.handlers), fragment);
    // return the fragment and all updates to use within its nodes
    return {
        content: fragment,
        updates
    };
};
const unroll = (info, { type, template, values })=>{
    const { length } = values;
    // interpolations can contain holes and arrays, so these need
    // to be recursively discovered
    unrollValues(info, values, length);
    let { entry } = info;
    // if the cache entry is either null or different from the template
    // and the type this unroll should resolve, create a new entry
    // assigning a new content fragment and the list of updates.
    if (!entry || entry.template !== template || entry.type !== type) info.entry = entry = createEntry(type, template);
    const { content, updates, wire } = entry;
    // even if the fragment and its nodes is not live yet,
    // it is already possible to update via interpolations values.
    for(let i = 0; i < length; i++)updates[i](values[i]);
    // if the entry was new, or representing a different template or type,
    // create a new persistent entity to use during diffing.
    // This is simply a DOM node, when the template has a single container,
    // as in `<p></p>`, or a "wire" in `<p></p><p></p>` and similar cases.
    return wire || (entry.wire = (0, _uwire.persistent)(content));
};
// the stack retains, per each interpolation value, the cache
// related to each interpolation value, or null, if the render
// was conditional and the value is not special (Array or Hole)
const unrollValues = ({ stack }, values, length)=>{
    for(let i = 0; i < length; i++){
        const hole = values[i];
        // each Hole gets unrolled and re-assigned as value
        // so that domdiff will deal with a node/wire, not with a hole
        if (hole instanceof Hole) values[i] = unroll(stack[i] || (stack[i] = createCache()), hole);
        else if ((0, _uarray.isArray)(hole)) unrollValues(stack[i] || (stack[i] = createCache()), hole, hole.length);
        else stack[i] = null;
    }
    if (length < stack.length) stack.splice(length);
};
function Hole(type, template, values) {
    this.type = type;
    this.template = template;
    this.values = values;
}

},{"umap":"b3ep2","uparser":"l3Oqg","uarray":"7ftea","uwire":"eGHCa","./handlers.js":"aEsZd","./node.js":"9Th3F","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"l3Oqg":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
const attr = /([^\s\\>"'=]+)\s*=\s*(['"]?)$/;
const empty = /^(?:area|base|br|col|embed|hr|img|input|keygen|link|menuitem|meta|param|source|track|wbr)$/i;
const node = /<[a-z][^>]+$/i;
const notNode = />[^<>]*$/;
const selfClosing = /<([a-z]+[a-z0-9:._-]*)([^>]*?)(\/>)/ig;
const trimEnd = /\s+$/;
const isNode = (template, i)=>0 < i-- && (node.test(template[i]) || !notNode.test(template[i]) && isNode(template, i));
const regular = (original, name, extra)=>empty.test(name) ? original : `<${name}${extra.replace(trimEnd, "")}></${name}>`;
exports.default = (template, prefix, svg)=>{
    const text = [];
    const { length } = template;
    for(let i = 1; i < length; i++){
        const chunk = template[i - 1];
        text.push(attr.test(chunk) && isNode(template, i) ? chunk.replace(attr, (_, $1, $2)=>`${prefix}${i - 1}=${$2 || '"'}${$1}${$2 ? "" : '"'}`) : `${chunk}<!--${prefix}${i - 1}-->`);
    }
    text.push(template[length - 1]);
    const output = text.join("").trim();
    return svg ? output : output.replace(selfClosing, regular);
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"7ftea":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "isArray", ()=>isArray);
parcelHelpers.export(exports, "indexOf", ()=>indexOf);
parcelHelpers.export(exports, "slice", ()=>slice);
const { isArray } = Array;
const { indexOf, slice } = [];

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"eGHCa":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "diffable", ()=>diffable);
parcelHelpers.export(exports, "persistent", ()=>persistent);
var _uarray = require("uarray");
const ELEMENT_NODE = 1;
const nodeType = 111;
const remove = ({ firstChild, lastChild })=>{
    const range = document.createRange();
    range.setStartAfter(firstChild);
    range.setEndAfter(lastChild);
    range.deleteContents();
    return firstChild;
};
const diffable = (node, operation)=>node.nodeType === nodeType ? 1 / operation < 0 ? operation ? remove(node) : node.lastChild : operation ? node.valueOf() : node.firstChild : node;
const persistent = (fragment)=>{
    const { childNodes } = fragment;
    const { length } = childNodes;
    if (length < 2) return length ? childNodes[0] : fragment;
    const nodes = (0, _uarray.slice).call(childNodes, 0);
    const firstChild = nodes[0];
    const lastChild = nodes[length - 1];
    return {
        ELEMENT_NODE,
        nodeType,
        firstChild,
        lastChild,
        valueOf () {
            if (childNodes.length !== length) {
                let i = 0;
                while(i < length)fragment.appendChild(nodes[i++]);
            }
            return fragment;
        }
    };
};

},{"uarray":"7ftea","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"aEsZd":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
// each mapped update carries the update type and its path
// the type is either node, attribute, or text, while
// the path is how to retrieve the related node to update.
// In the attribute case, the attribute name is also carried along.
parcelHelpers.export(exports, "handlers", ()=>handlers);
var _uarray = require("uarray");
var _udomdiff = require("udomdiff");
var _udomdiffDefault = parcelHelpers.interopDefault(_udomdiff);
var _uhandlers = require("uhandlers");
var _uwire = require("uwire");
// from a generic path, retrieves the exact targeted node
const reducePath = ({ childNodes }, i)=>childNodes[i];
// this helper avoid code bloat around handleAnything() callback
const diff = (comment, oldNodes, newNodes)=>(0, _udomdiffDefault.default)(comment.parentNode, // TODO: there is a possible edge case where a node has been
    //       removed manually, or it was a keyed one, attached
    //       to a shared reference between renders.
    //       In this case udomdiff might fail at removing such node
    //       as its parent won't be the expected one.
    //       The best way to avoid this issue is to filter oldNodes
    //       in search of those not live, or not in the current parent
    //       anymore, but this would require both a change to uwire,
    //       exposing a parentNode from the firstChild, as example,
    //       but also a filter per each diff that should exclude nodes
    //       that are not in there, penalizing performance quite a lot.
    //       As this has been also a potential issue with domdiff,
    //       and both lighterhtml and hyperHTML might fail with this
    //       very specific edge case, I might as well document this possible
    //       "diffing shenanigan" and call it a day.
    oldNodes, newNodes, (0, _uwire.diffable), comment);
// if an interpolation represents a comment, the whole
// diffing will be related to such comment.
// This helper is in charge of understanding how the new
// content for such interpolation/hole should be updated
const handleAnything = (comment)=>{
    let oldValue, text, nodes = [];
    const anyContent = (newValue)=>{
        switch(typeof newValue){
            // primitives are handled as text content
            case "string":
            case "number":
            case "boolean":
                if (oldValue !== newValue) {
                    oldValue = newValue;
                    if (!text) text = document.createTextNode("");
                    text.data = newValue;
                    nodes = diff(comment, nodes, [
                        text
                    ]);
                }
                break;
            // null, and undefined are used to cleanup previous content
            case "object":
            case "undefined":
                if (newValue == null) {
                    if (oldValue != newValue) {
                        oldValue = newValue;
                        nodes = diff(comment, nodes, []);
                    }
                    break;
                }
                // arrays and nodes have a special treatment
                if ((0, _uarray.isArray)(newValue)) {
                    oldValue = newValue;
                    // arrays can be used to cleanup, if empty
                    if (newValue.length === 0) nodes = diff(comment, nodes, []);
                    else if (typeof newValue[0] === "object") nodes = diff(comment, nodes, newValue);
                    else anyContent(String(newValue));
                    break;
                }
                // if the new value is a DOM node, or a wire, and it's
                // different from the one already live, then it's diffed.
                // if the node is a fragment, it's appended once via its childNodes
                // There is no `else` here, meaning if the content
                // is not expected one, nothing happens, as easy as that.
                if (oldValue !== newValue && "ELEMENT_NODE" in newValue) {
                    oldValue = newValue;
                    nodes = diff(comment, nodes, newValue.nodeType === 11 ? (0, _uarray.slice).call(newValue.childNodes) : [
                        newValue
                    ]);
                }
                break;
            case "function":
                anyContent(newValue(comment));
                break;
        }
    };
    return anyContent;
};
// attributes can be:
//  * ref=${...}      for hooks and other purposes
//  * aria=${...}     for aria attributes
//  * ?boolean=${...} for boolean attributes
//  * .dataset=${...} for dataset related attributes
//  * .setter=${...}  for Custom Elements setters or nodes with setters
//                    such as buttons, details, options, select, etc
//  * @event=${...}   to explicitly handle event listeners
//  * onevent=${...}  to automatically handle event listeners
//  * generic=${...}  to handle an attribute just like an attribute
const handleAttribute = (node, name /*, svg*/ )=>{
    switch(name[0]){
        case "?":
            return (0, _uhandlers.boolean)(node, name.slice(1), false);
        case ".":
            return (0, _uhandlers.setter)(node, name.slice(1));
        case "@":
            return (0, _uhandlers.event)(node, "on" + name.slice(1));
        case "o":
            if (name[1] === "n") return (0, _uhandlers.event)(node, name);
    }
    switch(name){
        case "ref":
            return (0, _uhandlers.ref)(node);
        case "aria":
            return (0, _uhandlers.aria)(node);
    }
    return (0, _uhandlers.attribute)(node, name /*, svg*/ );
};
function handlers(options) {
    const { type, path } = options;
    const node = path.reduceRight(reducePath, this);
    return type === "node" ? handleAnything(node) : type === "attr" ? handleAttribute(node, options.name /*, options.svg*/ ) : (0, _uhandlers.text)(node);
}

},{"uarray":"7ftea","udomdiff":"9UVlK","uhandlers":"ceEOD","uwire":"eGHCa","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9UVlK":[function(require,module,exports) {
/**
 * ISC License
 *
 * Copyright (c) 2020, Andrea Giammarchi, @WebReflection
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
 * OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */ /**
 * @param {Node} parentNode The container where children live
 * @param {Node[]} a The list of current/live children
 * @param {Node[]} b The list of future children
 * @param {(entry: Node, action: number) => Node} get
 * The callback invoked per each entry related DOM operation.
 * @param {Node} [before] The optional node used as anchor to insert before.
 * @returns {Node[]} The same list of future children.
 */ var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
exports.default = (parentNode, a, b, get, before)=>{
    const bLength = b.length;
    let aEnd = a.length;
    let bEnd = bLength;
    let aStart = 0;
    let bStart = 0;
    let map = null;
    while(aStart < aEnd || bStart < bEnd){
        // append head, tail, or nodes in between: fast path
        if (aEnd === aStart) {
            // we could be in a situation where the rest of nodes that
            // need to be added are not at the end, and in such case
            // the node to `insertBefore`, if the index is more than 0
            // must be retrieved, otherwise it's gonna be the first item.
            const node = bEnd < bLength ? bStart ? get(b[bStart - 1], -0).nextSibling : get(b[bEnd - bStart], 0) : before;
            while(bStart < bEnd)parentNode.insertBefore(get(b[bStart++], 1), node);
        } else if (bEnd === bStart) while(aStart < aEnd){
            // remove the node only if it's unknown or not live
            if (!map || !map.has(a[aStart])) parentNode.removeChild(get(a[aStart], -1));
            aStart++;
        }
        else if (a[aStart] === b[bStart]) {
            aStart++;
            bStart++;
        } else if (a[aEnd - 1] === b[bEnd - 1]) {
            aEnd--;
            bEnd--;
        } else if (a[aStart] === b[bEnd - 1] && b[bStart] === a[aEnd - 1]) {
            // this is a "shrink" operation that could happen in these cases:
            // [1, 2, 3, 4, 5]
            // [1, 4, 3, 2, 5]
            // or asymmetric too
            // [1, 2, 3, 4, 5]
            // [1, 2, 3, 5, 6, 4]
            const node = get(a[--aEnd], -1).nextSibling;
            parentNode.insertBefore(get(b[bStart++], 1), get(a[aStart++], -1).nextSibling);
            parentNode.insertBefore(get(b[--bEnd], 1), node);
            // mark the future index as identical (yeah, it's dirty, but cheap 👍)
            // The main reason to do this, is that when a[aEnd] will be reached,
            // the loop will likely be on the fast path, as identical to b[bEnd].
            // In the best case scenario, the next loop will skip the tail,
            // but in the worst one, this node will be considered as already
            // processed, bailing out pretty quickly from the map index check
            a[aEnd] = b[bEnd];
        } else {
            // the map requires an O(bEnd - bStart) operation once
            // to store all future nodes indexes for later purposes.
            // In the worst case scenario, this is a full O(N) cost,
            // and such scenario happens at least when all nodes are different,
            // but also if both first and last items of the lists are different
            if (!map) {
                map = new Map;
                let i = bStart;
                while(i < bEnd)map.set(b[i], i++);
            }
            // if it's a future node, hence it needs some handling
            if (map.has(a[aStart])) {
                // grab the index of such node, 'cause it might have been processed
                const index = map.get(a[aStart]);
                // if it's not already processed, look on demand for the next LCS
                if (bStart < index && index < bEnd) {
                    let i = aStart;
                    // counts the amount of nodes that are the same in the future
                    let sequence = 1;
                    while(++i < aEnd && i < bEnd && map.get(a[i]) === index + sequence)sequence++;
                    // effort decision here: if the sequence is longer than replaces
                    // needed to reach such sequence, which would brings again this loop
                    // to the fast path, prepend the difference before a sequence,
                    // and move only the future list index forward, so that aStart
                    // and bStart will be aligned again, hence on the fast path.
                    // An example considering aStart and bStart are both 0:
                    // a: [1, 2, 3, 4]
                    // b: [7, 1, 2, 3, 6]
                    // this would place 7 before 1 and, from that time on, 1, 2, and 3
                    // will be processed at zero cost
                    if (sequence > index - bStart) {
                        const node = get(a[aStart], 0);
                        while(bStart < index)parentNode.insertBefore(get(b[bStart++], 1), node);
                    } else parentNode.replaceChild(get(b[bStart++], 1), get(a[aStart++], -1));
                } else aStart++;
            } else parentNode.removeChild(get(a[aStart++], -1));
        }
    }
    return b;
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"ceEOD":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Foreign", ()=>Foreign);
parcelHelpers.export(exports, "foreign", ()=>foreign);
parcelHelpers.export(exports, "aria", ()=>aria);
parcelHelpers.export(exports, "attribute", ()=>attribute);
parcelHelpers.export(exports, "boolean", ()=>boolean);
parcelHelpers.export(exports, "data", ()=>data);
parcelHelpers.export(exports, "event", ()=>event);
parcelHelpers.export(exports, "ref", ()=>ref);
parcelHelpers.export(exports, "setter", ()=>setter);
parcelHelpers.export(exports, "text", ()=>text);
var _uarray = require("uarray");
// flag for foreign checks (slower path, fast by default)
let useForeign = false;
class Foreign {
    constructor(handler, value){
        useForeign = true;
        this._ = (...args)=>handler(...args, value);
    }
}
const foreign = (handler, value)=>new Foreign(handler, value);
const aria = (node)=>(values)=>{
        for(const key in values){
            const name = key === "role" ? key : `aria-${key}`;
            const value = values[key];
            if (value == null) node.removeAttribute(name);
            else node.setAttribute(name, value);
        }
    };
const attribute = (node, name)=>{
    let oldValue, orphan = true;
    const attributeNode = document.createAttributeNS(null, name);
    return (newValue)=>{
        if (oldValue !== newValue) {
            oldValue = newValue;
            if (oldValue == null) {
                if (!orphan) {
                    node.removeAttributeNode(attributeNode);
                    orphan = true;
                }
            } else {
                const value = useForeign && newValue instanceof Foreign ? newValue._(node, name) : newValue;
                if (value == null) {
                    if (!orphan) node.removeAttributeNode(attributeNode);
                    orphan = true;
                } else {
                    attributeNode.value = value;
                    if (orphan) {
                        node.setAttributeNodeNS(attributeNode);
                        orphan = false;
                    }
                }
            }
        }
    };
};
const boolean = (node, key, oldValue)=>(newValue)=>{
        if (oldValue !== !!newValue) {
            // when IE won't be around anymore ...
            // node.toggleAttribute(key, oldValue = !!newValue);
            if (oldValue = !!newValue) node.setAttribute(key, "");
            else node.removeAttribute(key);
        }
    };
const data = ({ dataset })=>(values)=>{
        for(const key in values){
            const value = values[key];
            if (value == null) delete dataset[key];
            else dataset[key] = value;
        }
    };
const event = (node, name)=>{
    let oldValue, lower, type = name.slice(2);
    if (!(name in node) && (lower = name.toLowerCase()) in node) type = lower.slice(2);
    return (newValue)=>{
        const info = (0, _uarray.isArray)(newValue) ? newValue : [
            newValue,
            false
        ];
        if (oldValue !== info[0]) {
            if (oldValue) node.removeEventListener(type, oldValue, info[1]);
            if (oldValue = info[0]) node.addEventListener(type, oldValue, info[1]);
        }
    };
};
const ref = (node)=>{
    let oldValue;
    return (value)=>{
        if (oldValue !== value) {
            oldValue = value;
            if (typeof value === "function") value(node);
            else value.current = node;
        }
    };
};
const setter = (node, key)=>key === "dataset" ? data(node) : (value)=>{
        node[key] = value;
    };
const text = (node)=>{
    let oldValue;
    return (newValue)=>{
        if (oldValue != newValue) {
            oldValue = newValue;
            node.textContent = newValue == null ? "" : newValue;
        }
    };
};

},{"uarray":"7ftea","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9Th3F":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "createFragment", ()=>createFragment);
parcelHelpers.export(exports, "createWalker", ()=>createWalker);
var _createContent = require("@ungap/create-content");
var _createContentDefault = parcelHelpers.interopDefault(_createContent);
// this "hack" tells the library if the browser is IE11 or old Edge
const isImportNodeLengthWrong = document.importNode.length != 1;
const createFragment = isImportNodeLengthWrong ? (text, type, normalize)=>document.importNode((0, _createContentDefault.default)(text, type, normalize), true) : (0, _createContentDefault.default);
const createWalker = isImportNodeLengthWrong ? (fragment)=>document.createTreeWalker(fragment, 129, null, false) : (fragment)=>document.createTreeWalker(fragment, 129);

},{"@ungap/create-content":"4xeIY","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"4xeIY":[function(require,module,exports) {
/*! (c) Andrea Giammarchi - ISC */ var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var createContent = function(document1) {
    "use strict";
    var FRAGMENT = "fragment";
    var TEMPLATE = "template";
    var HAS_CONTENT = "content" in create(TEMPLATE);
    var createHTML = HAS_CONTENT ? function(html) {
        var template = create(TEMPLATE);
        template.innerHTML = html;
        return template.content;
    } : function(html) {
        var content = create(FRAGMENT);
        var template = create(TEMPLATE);
        var childNodes = null;
        if (/^[^\S]*?<(col(?:group)?|t(?:head|body|foot|r|d|h))/i.test(html)) {
            var selector = RegExp.$1;
            template.innerHTML = "<table>" + html + "</table>";
            childNodes = template.querySelectorAll(selector);
        } else {
            template.innerHTML = html;
            childNodes = template.childNodes;
        }
        append(content, childNodes);
        return content;
    };
    return function createContent(markup, type) {
        return (type === "svg" ? createSVG : createHTML)(markup);
    };
    function append(root, childNodes) {
        var length = childNodes.length;
        while(length--)root.appendChild(childNodes[0]);
    }
    function create(element) {
        return element === FRAGMENT ? document1.createDocumentFragment() : document1.createElementNS("http://www.w3.org/1999/xhtml", element);
    }
    // it could use createElementNS when hasNode is there
    // but this fallback is equally fast and easier to maintain
    // it is also battle tested already in all IE
    function createSVG(svg) {
        var content = create(FRAGMENT);
        var template = create("div");
        template.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg">' + svg + "</svg>";
        append(content, template.firstChild.childNodes);
        return content;
    }
}(document);
exports.default = createContent;

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"3NusC":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Button", ()=>Button);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonStyle = require("./button.style");
class Button extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _buttonStyle.ButtonStyle);
    })();
    static #_1 = (()=>{
        this.tagName = "button";
    })();
    static define(tagName) {
        if (tagName.toLocaleLowerCase() === "button") {
            this.tagName = "button";
            this.initStyle();
            return;
        }
        super.define(tagName);
    }
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button.style":"dIaU3","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"dIaU3":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonStyle", ()=>ButtonStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class ButtonStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue",
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        return `
        border: 0;
        font-size: 1em;
        line-height: 1;
        font-weight: bold;
        text-decoration: none;
        outline: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        height: 2em;
        padding-left: 0.4em;
        padding-right: 0.4em;
        cursor: pointer;
        transition: 0.2s;
        box-sizing: border-box;
        -webkit-tap-highlight-color: rgba(0,0,0,0);
        &[disabled]:hover {
            cursor: not-allowed;
        }
        a {
            text-decoration: none;
        }
        ${(0, _style.lift)({
            level: 1
        })}
        &:hover {
            ${(0, _style.lift)({
            level: 2
        })};
        }
        &:active {
            ${(0, _style.lift)({
            level: 1
        })};
        }
        ${this.style(style)}
        `.trim();
    }
    static style(style = {}) {
        return `
        ${this._color(style)}
        ${this._borderRadius(style)}
        `.trim();
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        let css = `
        ${(0, _style.bgColorInt)({
            color: style.color
        })}
        `.trim();
        return css;
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        let css = `
        border-radius: ${style.borderRadius};
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"808uY":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonGroup", ()=>ButtonGroup);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonGroupStyle = require("./button-group.style");
class ButtonGroup extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _buttonGroupStyle.ButtonGroupStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button-group.style":"8saZA","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"8saZA":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonGroupStyle", ()=>ButtonGroupStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
class ButtonGroupStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        display: inline-flex;
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        if (style.borderRadius == undefined) return "";
        let css = `
        > * {
            border-radius: 0;
            &:first-of-type {
                border-radius: ${style.borderRadius} 0 0 ${style.borderRadius};
            }
            &:last-of-type {
                border-radius: 0 ${style.borderRadius} ${style.borderRadius} 0;
            }
        }
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"5ibGP":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonPin", ()=>ButtonPin);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonPinStyle = require("./button-pin.style");
class ButtonPin extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _buttonPinStyle.ButtonPinStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button-pin.style":"c3zto","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"c3zto":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonPinStyle", ()=>ButtonPinStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonStyle = require("./button.style");
class ButtonPinStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        ${(0, _buttonStyle.ButtonStyle).css(style)}
        user-select: none;
        border-radius: 50%;
        min-width: 2em;
        min-height: 2em;
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        if (style.color == undefined) return "";
        let css = `
        ${(0, _buttonStyle.ButtonStyle).style(style)}
        border-radius: 50%;
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button.style":"dIaU3","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"eKEy4":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonSquare", ()=>ButtonSquare);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonSquareStyle = require("./button-square.style");
class ButtonSquare extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _buttonSquareStyle.ButtonSquareStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.classList.add("button");
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button-square.style":"fkG8e","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"fkG8e":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ButtonSquareStyle", ()=>ButtonSquareStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _buttonStyle = require("./button.style");
var _style = require("../../style");
class ButtonSquareStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue",
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        ${(0, _buttonStyle.ButtonStyle).css(style)}
        user-select: none;
        ${(0, _style.aspectRatio)("1/1")}
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${(0, _buttonStyle.ButtonStyle).style(style)}
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./button.style":"dIaU3","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"iMJm5":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Card", ()=>Card);
var _adapter = require("@nitipit/adapter/src/adapter");
var _cardStyle = require("./card.style");
class Card extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _cardStyle.CardStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./card.style":"ciVqa","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"ciVqa":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "CardStyle", ()=>CardStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class CardStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "#eee",
            borderRadius: "4px"
        };
    })();
    static css(style) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        display: block;
        ${(0, _style.lift)({
            level: 3
        })}
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._color(style)}
        ${this._borderRadius(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return `
        ${(0, _style.bgColor)(style.color)}
        `.trim();
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        return `
        border-radius: ${style.borderRadius};
        overflow: hidden;
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"hO2dk":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Checkbox", ()=>Checkbox);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _checkboxStyle = require("./checkbox.style");
class Checkbox extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _checkboxStyle.CheckboxStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.el = {
            checkbox: null
        };
        this.el.checkbox = this.querySelector('input[type="checkbox"]') || (0, _uhtml.html)`<input type="checkbox">`;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
        ${this.el.checkbox}
        <span></span>
        `);
        this.el.checkbox = this.querySelector('input[type="checkbox"]');
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./checkbox.style":"lRNeL","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"lRNeL":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "CheckboxStyle", ()=>CheckboxStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
const Color = require("30ca9c6e4fd88b63");
class CheckboxStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            bgColor: "#ccc",
            activeColor: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        position: relative;
        width: 1em;
        height: 1em;
        user-select: none;
        display: inline-block;

        /* Hide the browser's default checkbox */
        input {
            opacity: 0;
            cursor: pointer;
            width: 1em;
            height: 1em;
            margin: 0;
            position: absolute;
            top: 1;
            left: 0;
            z-index: 1;
        }

        /* Create a custom checkbox */
        span {
            position: absolute;
            top: 0;
            left: 0;
            width: 1em;
            height: 1em;
            box-shadow: 0 1px 1px 0 grey;
        }

        /* Create the checkmark/indicator (hidden when not checked) */
        span:after {
            content: "";
            position: absolute;
            display: none;
        }

        /* Show the checkmark when checked */
        input:checked ~ span:after {
            display: block;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._bgColor(style)}
        ${this._activeColor(style)}
        `.trim();
        return css;
    }
    static _bgColor(style = {}) {
        if (style.bgColor == undefined) return "";
        return `
        span {
            background-color: ${style.bgColor};
        }
        `.trim();
    }
    static _activeColor(style = {}) {
        if (style.activeColor == undefined) return "";
        let markColor = "black";
        if (Color(style.activeColor).isDark()) markColor = "white";
        return `
        /* Style the checkmark/indicator */
        span:after {
            border: solid ${markColor};
            left: 0.25em;
            width: 0.3em;
            height: 0.6em;
            border-width: 0 0.2em 0.2em 0;
            transform: rotate(45deg);
        }

        /* When the checkbox is checked, add background color */
        input:checked ~ span {
            background-color: ${style.activeColor};
        }

        /* On mouse-over, add background color */
        &:hover input ~ span {
            background-color: ${Color(style.activeColor).lighten(0.2)}
        }
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","30ca9c6e4fd88b63":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"4HNBJ":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Input", ()=>Input);
var _adapter = require("@nitipit/adapter/src/adapter");
var _inputStyle = require("./input.style");
class Input extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _inputStyle.InputStyle);
    })();
}
(0, _adapter.addStyle)`
input {
    ${(0, _inputStyle.InputStyle).css()}
}`;

},{"@nitipit/adapter/src/adapter":"1Fra8","./input.style":"3EGlv","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"3EGlv":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputStyle", ()=>InputStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
class InputStyle extends (0, _adapter.StyleClass) {
    static css(style = {}) {
        return `
        font-size: 1em;
        border: 1px solid grey;
        border-radius: 0.2em;
        padding: 0.4em;
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"ecTia":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputDate", ()=>InputDate);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _inputDateStyle = require("./input-date.style");
class InputDate extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _inputDateStyle.InputDateStyle);
    })();
    constructor(){
        super();
        this.icon = (0, _uhtml.svg)`
    <svg xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16" style="width: 1em; height: 1em;">
        <g fill="currentColor">
            <path d="M2.969 1.01c-1.053 0-2 .846-2 1.938v10.115c0 1.092.947 1.937 2 1.937H13c1.052 0 2-.845 2-1.937V2.948c0-1.092-.948-1.937-2-1.937zm0 3.99H5v2H2.969zM6 5h3v2H6zm4 0h3v2h-3zM2.969 8H5v2H2.969zM6 8h3v2H6zm4 0h3v2h-3zm-7.031 3H5v2H2.969zM6 11h3v2H6zm4 0h3v2h-3z" overflow="visible" />
            <path d="M10 8h3v2h-3z" overflow="visible" opacity=".35" />
        </g>
    </svg>
    `;
        this.el = {
            input: null,
            display: null
        };
        this.el.input = this.querySelector('input[type="date"]') || (0, _uhtml.html)`<input type="date">`;
        this.render();
    }
    onChange(event) {
        let inputDate = event.target;
        this.el.display.innerText = inputDate.value;
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            <div el="icon">${this.icon}</div>
            ${this.el.input}
            <span el="display"></span>
        `);
        this.el.input = this.querySelector("input");
        this.el.input.addEventListener("change", (event)=>{
            this.onChange(event);
        });
        this.el.display = this.querySelector('span[el="display"]');
        this.el.display.innerText = this.el.input.value;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./input-date.style":"87rPW","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"87rPW":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputDateStyle", ()=>InputDateStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
class InputDateStyle extends (0, _adapter.StyleClass) {
    static css(style = {}) {
        const css = `
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        position: relative;

        [el="icon"] {
            line-height: 0.8;
            font-size: 2em;
        }

        input[type="date"] {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
            box-sizing: border-box;
            padding: 0;
            z-index: 100;
        }

        input[type="date"]::-webkit-calendar-picker-indicator {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            cursor: pointer;
        }

        span[el="display"] {
            display: inline-flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            padding: 0 0.5em;
            margin-left: 0.5em;
            border: 2px solid;
            border-radius: 0.2em;
            min-width: 7rem;
            height: 2em;
            line-height: 1;

        }
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"8bUj3":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputNumber", ()=>InputNumber);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _inputNumberStyle = require("./input-number.style");
class InputNumber extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _inputNumberStyle.InputNumberStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.stepIntervalThreshold = null;
        this._stepIntervalThreshold = null;
        this.stepInterval = null;
        this._stepInterval = null;
        this.stepChangeDelay = null;
        this.stepChangeTimeout = null;
        this.el = {
            input: null
        };
        this.stepIntervalThreshold = parseInt(this.getAttribute("stepIntervalThreshold") || "700");
        this.stepInterval = parseInt(this.getAttribute("stepInterval") || "100");
        this.stepChangeDelay = parseInt(this.getAttribute("stepChangeDelay") || "1000");
        this.el.input = this.querySelector('input[type="number"]') || (0, _uhtml.html)`<input type="number">`;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            ${this.el.input}
            <button el="down"
                @mousedown=${()=>this.stepDownStart()}
                @mouseup=${()=>this.pressStop()}
                @mouseout=${()=>this.pressStop()}
            >-</button>
            <button el="up"
                @mousedown=${()=>this.stepUpStart()}
                @mouseup=${()=>this.pressStop()}
                @mouseout=${()=>this.pressStop()}
            >+</button>
        `);
        this.el.input = this.querySelector('input[type="number"]');
        this.el.input.addEventListener("change", ()=>{
            this.oldValue = this.el.input.value;
            this.dispatchEvent(new Event("change"));
        });
    }
    emitStepChangeEvent() {
        clearTimeout(this.stepChangeTimeout);
        if (this.oldValue == this.el.input.value) return;
        this.stepChangeTimeout = setTimeout(()=>{
            this.oldValue = this.el.input.value;
            this.dispatchEvent(new Event("change"));
        }, this.stepChangeDelay);
    }
    stepUpStart() {
        this.el.input.stepUp();
        this._stepIntervalThreshold = setTimeout(()=>{
            this._stepInterval = setInterval(()=>{
                this.el.input.stepUp();
            }, this.stepInterval);
        }, this.stepIntervalThreshold);
    }
    stepDownStart() {
        this.el.input.stepDown();
        this._stepIntervalThreshold = setTimeout(()=>{
            this._stepInterval = setInterval(()=>{
                this.el.input.stepDown();
            }, this.stepInterval);
        }, this.stepIntervalThreshold);
    }
    pressStop() {
        if (this._stepIntervalThreshold) {
            clearTimeout(this._stepIntervalThreshold);
            clearInterval(this._stepInterval);
            this.emitStepChangeEvent();
        }
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./input-number.style":"a2Vst","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"a2Vst":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputNumberStyle", ()=>InputNumberStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _inputStyle = require("./input.style");
var _buttonSquareStyle = require("../button/button-square.style");
class InputNumberStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const css = `
        display: inline-flex;
        height: 2em;
        min-width: 7em;
        input[type="number"] {
            ${(0, _inputStyle.InputStyle).css()}
            &::-webkit-inner-spin-button {
                -webkit-appearance: none;
            }
            -moz-appearance: textfield;
            text-align: center;
            width: 4em;
            border-radius: 0.2em 0 0 0.2em;
        }
        button[el="down"] {
            ${(0, _buttonSquareStyle.ButtonSquareStyle).css({
            color: style.color
        })}
            border-radius: 0;
            width: 2em;
        }
        button[el="up"] {
            ${(0, _buttonSquareStyle.ButtonSquareStyle).css({
            color: style.color
        })}
            border-radius: 0 4px 4px 0;
            width: 2em;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._color(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return `
        button[el="down"] {
            ${(0, _buttonSquareStyle.ButtonSquareStyle).style({
            color: style.color
        })}
        }
        button[el="up"] {
            ${(0, _buttonSquareStyle.ButtonSquareStyle).style({
            color: style.color
        })}
        }
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./input.style":"3EGlv","../button/button-square.style":"fkG8e","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"6Sae6":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputNumberCenter", ()=>InputNumberCenter);
var _inputNumber = require("./input-number");
var _uhtml = require("uhtml");
var _inputNumberCenterStyle = require("./input-number-center.style");
class InputNumberCenter extends (0, _inputNumber.InputNumber) {
    static #_ = (()=>{
        this.Style = (0, _inputNumberCenterStyle.InputNumberCenterStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            <button el="down"
                @mousedown=${()=>this.stepDownStart()}
                @mouseup=${()=>this.pressStop()}
                @mouseout=${()=>this.pressStop()}
            >-</button>
            ${this.el.input}
            <button el="up"
                @mousedown=${()=>this.stepUpStart()}
                @mouseup=${()=>this.pressStop()}
                @mouseout=${()=>this.pressStop()}
            >+</button>
        `);
        this.el.input = this.querySelector('input[type="number"]');
        this.el.input.addEventListener("change", ()=>{
            this.oldValue = this.el.input.value;
            this.dispatchEvent(new Event("change"));
        });
    }
}

},{"./input-number":"8bUj3","uhtml":"if09d","./input-number-center.style":"9PmWu","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9PmWu":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputNumberCenterStyle", ()=>InputNumberCenterStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _inputNumberStyle = require("./input-number.style");
class InputNumberCenterStyle extends (0, _adapter.StyleClass) {
    static css(style = {}) {
        const css = `
        ${(0, _inputNumberStyle.InputNumberStyle).css()}
        input[type="number"] {
            border-radius: 0;
        }
        button[el="up"] {
            z-index: 1;
        }
        button[el="down"] {
            border-radius: 0.2em 0 0 0.2em;
            z-index: 1;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${(0, _inputNumberStyle.InputNumberStyle).style(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        const css = `
        ${(0, _inputNumberStyle.InputNumberStyle)._color(style)}
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./input-number.style":"a2Vst","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"hkfMk":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputRadio", ()=>InputRadio);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _inputRadioStyle = require("./input-radio.style");
class InputRadio extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _inputRadioStyle.InputRadioStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.el = {
            input: null
        };
        this.el.input = this.querySelector('input[type="radio"]') || (0, _uhtml.html)`<input type="radio">`;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
        ${this.el.input}
        <span></span>
        `);
        this.el.input = this.querySelector('input[type="radio"]');
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./input-radio.style":"5jwEi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"5jwEi":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputRadioStyle", ()=>InputRadioStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var Color = require("3d36b47ac28af1e9");
class InputRadioStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "#ccc",
            boxShadowColor: "#777",
            activeColor: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let markDotColor = "black";
        if (Color(style.activeColor).isDark()) markDotColor = "white";
        const css = `
        position: relative;
        display: inline-block;
        font-size: 1em;
        user-select: none;
        width: 1.1em;
        height: 1.1em;
        input {
            position: absolute;
            z-index: 1;
            top: 0;
            left: 0;
            opacity: 0;
            cursor: pointer;
            width: 1.1em;
            height: 1.1em;
            vertical-align: middle;
        }

        /* Create a custom radio button */
        span {
            position: absolute;
            top: 0;
            left: 0;
            width: 1.1em;
            height: 1.1em;
            border-radius: 50%;
        }

        /* Create the indicator (the dot/circle - hidden when not checked) */
        span:after {
            content: "";
            position: absolute;
            display: none;
        }

        /* Show the indicator (dot/circle) when checked */
        input:checked ~ span:after {
            display: block;
        }

        /* Style the indicator (dot/circle) */
        span:after {
            top: 0.35em;
            left: 0.35em;
            width: 0.4em;
            height: 0.4em;
            border-radius: 50%;
            background-color: ${markDotColor};
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._color(style)}
        ${this._boxShadowColor(style)}
        ${this._activeColor(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return `
        span {
            background-color: ${style.color};
        }
        `.trim();
    }
    static _boxShadowColor(style = {}) {
        if (style.boxShadowColor == undefined) return "";
        return `
        span {
            box-shadow: 0 1px 1px 0 ${style.boxShadowColor};
        }`.trim();
    }
    static _activeColor(style = {}) {
        if (style.activeColor == undefined) return "";
        return `
        /* On mouse-over, add a background color */
        &:hover input ~ span {
            background-color: ${Color(style.activeColor).lighten(0.2).saturate(0.2)};
        }

        /* When the radio button is checked, add background color */
        input:checked ~ span {
            background-color: ${style.activeColor};
        }`.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","3d36b47ac28af1e9":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9RCxA":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputTag", ()=>InputTag);
var _adapter = require("@nitipit/adapter/src/adapter");
var _inputTagStyle = require("./input-tag.style");
var _tagx = require("../tag/tagx");
class InputTagX extends (0, _tagx.TagX) {
}
class InputTag extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _inputTagStyle.InputTagStyle);
    })();
    static define(tagName) {
        (0, _adapter.define)(`${tagName}-tagx`, InputTagX);
        (0, _adapter.addStyle)`
        ${InputTagX.tagName} {
            margin: 0.3em 0.2em;
        }
        `;
        super.define(tagName);
    }
    static tagStyle(style) {
        super.tagStyle(style);
        InputTagX.tagStyle({
            color: style.tagColor,
            borderRadius: style.tagBorderRadius
        });
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
        InputTagX.classStyle(class_, {
            color: style.tagColor,
            borderRadius: style.tagBorderRadius
        });
    }
    addStyle(style) {
        super.addStyle(style);
        for (let tagx of this.querySelectorAll(InputTagX.tagName))tagx.addStyle({
            color: style.tagColor,
            borderRadius: style.tagBorderRadius
        });
    }
    get tags() {
        let tags = [];
        let tag;
        for (tag of this.querySelectorAll(`${this.tagName}-tagx`))tags.push(tag.text.trim());
        return tags;
    }
    set tags(tags) {
        this.clearTags();
        this.addTags(tags);
    }
    constructor(){
        super();
        this.el = {
            input: null
        };
        this.el.input = document.createElement("div");
        this.el.input.setAttribute("contenteditable", true);
        this.appendChild(this.el.input);
        this.addEventListener("click", ()=>{
            this.el.input.focus();
        });
        this.el.input.addEventListener("keydown", (event)=>{
            this.keydown(event);
        });
        this.el.input.addEventListener("blur", (event)=>{
            this.blur();
        });
    }
    keydown(event) {
        if (event.key === "Enter") {
            this.addTag(this.el.input.innerText.trim());
            this.el.input.innerText = "";
        } else if (event.key === "Backspace") {
            if (this.el.input.innerText.trim() === "") this.el.input.previousSibling.remove();
        }
    }
    blur() {
        this.addTag(this.el.input.innerText.trim());
        this.el.input.innerText = "";
    }
    addTag(value) {
        if (value == "") return;
        let el;
        for (el of this.querySelectorAll(`${this.tagName}-tagx`)){
            el;
            if (el.text.trim() == value) return;
        }
        let tagx = new InputTagX;
        this.insertBefore(tagx, this.el.input);
        tagx.text = value;
        tagx.addEventListener("remove", (event)=>{
            this.dispatchEvent(new CustomEvent("remove", {
                detail: {
                    tagx: event.target
                }
            }));
        });
    }
    addTags(values) {
        for (let value of values)this.addTag(value);
    }
    clearTags() {
        for (let tagx of this.querySelectorAll(InputTagX.tagName))tagx.remove();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./input-tag.style":"eJsmb","../tag/tagx":"dovaj","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"eJsmb":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "InputTagStyle", ()=>InputTagStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _input = require("./input");
class InputTagStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            tagColor: "blue",
            tagBorderRadius: "4px"
        };
    })();
    static css(style) {
        const css = `
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        cursor: text;
        border: 1px solid grey;
        border-radius: 4px;
        background: white;
        min-height: 2em;
        min-width: 150px;
        padding: 0.2em;

        div[contenteditable="true"] {
            display: flex;
            align-items: center;
            outline: none;
            height: auto;
            border: 0;
            margin-left: 0.2em;
        }
        `.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./input":"4HNBJ","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"dovaj":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TagX", ()=>TagX);
var _tag = require("./tag");
var _tagxStyle = require("./tagx.style");
var _uhtml = require("uhtml");
class TagX extends (0, _tag.Tag) {
    static #_ = (()=>{
        this.Style = (0, _tagxStyle.TagXStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    get text() {
        return this._text;
    }
    set text(value) {
        this._text = value;
        this.el.text.innerText = value;
    }
    constructor(){
        super();
        this.el = {
            text: null
        };
        this._text = this.innerText;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            <span el="text">${this.text}</span>
            <span el="remove" @click=${()=>{
            this.remove();
        }}>x</span>
        `);
        this.el.text = this.querySelector('span[el="text"]');
    }
    remove() {
        this.dispatchEvent(new Event("remove"));
        super.remove();
    }
}

},{"./tag":"1o7hu","./tagx.style":"eB6rq","uhtml":"if09d","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"1o7hu":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Tag", ()=>Tag);
var _adapter = require("@nitipit/adapter/src/adapter");
var _tagStyle = require("./tag.style");
class Tag extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _tagStyle.TagStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./tag.style":"iouaK","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"iouaK":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TagStyleParam", ()=>TagStyleParam);
parcelHelpers.export(exports, "TagStyle", ()=>TagStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
const Color = require("e0c0bcad5e442649");
class TagStyleParam {
}
class TagStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            color: "blue",
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        display: inline-flex;
        align-items: center;
        padding: 0.1em 0.4em;
        font-size: 0.9em;
        line-height: unset;
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._color(style)}
        ${this._borderRadius(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return `
        ${(0, _style.bgColor)(style.color)}
        box-shadow: 0 0.17em 0 0 ${Color(style.color).darken(0.5)};
        `.trim();
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        return `
        border-radius: ${style.borderRadius};
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","e0c0bcad5e442649":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"eB6rq":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TagXStyle", ()=>TagXStyle);
var _tagStyle = require("./tag.style");
var _style = require("../../style");
const Color = require("a61cf1d121fe38fd");
class TagXStyle extends (0, _tagStyle.TagStyle) {
    static #_ = (()=>{
        this.default = {
            color: "blue",
            borderRadius: "4px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        ${super.css(style)}
        padding-right: 0;
        [el="remove"] {
            margin-left: 0.3em;
            padding-left: 0.4em;
            padding-right: 0.5em;
            font-weight: bold;
            border-left: 1px solid;
            cursor: pointer;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._color(style)}
        ${this._borderRadius(style)}
        `.trim();
        return css;
    }
    static _color(style = {}) {
        if (style.color == undefined) return "";
        return `
        ${(0, _style.bgColorInt)({
            color: style.color
        })}
        box-shadow: 0 0.17em 0 0 ${Color(style.color).darken(0.5)};
        `.trim();
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        return super._borderRadius(style);
    }
}

},{"./tag.style":"iouaK","../../style":"72rKO","a61cf1d121fe38fd":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"kupAp":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Menu", ()=>Menu);
var _adapter = require("@nitipit/adapter/src/adapter");
var _menuStyle = require("./menu.style");
class Menu extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _menuStyle.MenuStyle);
    })();
    constructor(){
        super();
        let a_items = this.querySelectorAll("a");
        for (let item of a_items){
            let innerHTML = item.innerHTML;
            let divContent = document.createElement("div");
            let divArrow = document.createElement("div");
            let caret = document.createElement("i");
            divContent.classList.add("content");
            divArrow.classList.add("arrow");
            item.innerHTML = "";
            divContent.innerHTML = innerHTML;
            item.append(divContent);
            item.append(divArrow);
            if (item.closest("li").querySelector("ul")) divArrow.append(caret);
            item.addEventListener("click", (event)=>{
                this.toggleShow(event.currentTarget);
            });
            if (item.classList.contains("show")) this._show(item.parentElement);
        }
    }
    toggleShow(a) {
        if (a.classList.contains("show")) this._hide(a.parentElement);
        else this._show(a.parentElement);
    }
    _hide(li) {
        for (let a of li.querySelectorAll("a")){
            a.classList.remove("show");
            let ul = a.parentElement.querySelector("ul");
            if (!ul) continue;
            ul.style.height = `${ul.scrollHeight}px`;
            // setTimeout to create height transition.
            setTimeout(function(ul) {
                ul.style.height = "0px";
            }, 0, ul);
        }
    }
    _show(li) {
        let a = li.querySelector("a");
        a.classList.add("show");
        let ul = a.closest(`ul, ${this.tagName}`);
        ul.style.height = "auto";
        ul = li.querySelector("ul");
        if (!ul) return;
        ul.style.height = `${ul.scrollHeight}px`;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./menu.style":"lzKII","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"lzKII":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "MenuStyle", ()=>MenuStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
const Color = require("8a16d89678c0d8a0");
class MenuStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            hoverColor: "blue",
            arrowColor: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const css = `
        display: block;
        padding: 0;
        margin: 0;
        border: 1px solid blue;
        border-radius: 0.2em;

        .arrow i {
            font-size: 1.2em;
            float: right;
            border-left: 0.25em solid transparent;
            border-right: 0.25em solid transparent;
            will-change: transform;
            transform: rotateZ(90deg);
            transition: transform 0.2s;
        }

        ul {
            margin: 0;
            padding-left: 1em;
            transition: height 0.2s;
            will-change: transition;
        }

        > ul {
            padding-left: 0;
        }

        li {
            list-style: none;
            display: block;
            overflow-y: hidden;
            overflow-x: hidden;
        }

        a {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 0.5em 1em;
            div.content {
                width: 100%;
            }
            div.arrow {
                min-width: 1em;
            }
        }

        a ~ ul {
            height: 0;
        }

        a.show {
            .arrow i {
                transform: rotateZ(180deg);
            }
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._hoverColor(style)}
        ${this._arrowColor(style)}
        `.trim();
        return css;
    }
    static _hoverColor(style = {}) {
        if (style.hoverColor == undefined) return "";
        let arrowColor = "black";
        if (Color(style.hoverColor).isDark()) arrowColor = "white";
        return `
        a {
            -webkit-tap-highlight-color: ${Color(style.hoverColor)};
        }
        a:hover {
            ${(0, _style.bgColor)(style.hoverColor)};
            .arrow i {
                border-bottom-color: ${arrowColor};
            }
        }
        `.trim();
    }
    static _arrowColor(style = {}) {
        if (style.arrowColor == undefined) return "";
        return `
        .arrow i {
            border-bottom: 0.25em solid ${style.arrowColor};
        }
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","8a16d89678c0d8a0":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2e4fD":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ProgressBar", ()=>ProgressBar);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _progressBarStyle = require("./progress-bar.style");
class ProgressBar extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _progressBarStyle.ProgressBarStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.max = 100;
        this.render();
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`<div el="progress"></div>`);
        this.max = parseFloat(this.getAttribute("max")) || this.max;
        this.value = parseFloat(this.getAttribute("value"));
    }
    set value(value) {
        if (typeof value != "number") value = parseFloat(value);
        this._value = value;
        if (isNaN(value)) this.setLoop();
        else this.setProgress(value);
    }
    get value() {
        return this._value;
    }
    setLoop() {
        this.classList.remove("value");
        this.classList.add("loop");
    }
    setProgress(value) {
        this.classList.remove("loop");
        this.classList.add("value");
        let progress = this.querySelector('[el="progress"]');
        progress.style.width = `${value / this.max * 100}%`;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./progress-bar.style":"gAeGy","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"gAeGy":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ProgressBarStyle", ()=>ProgressBarStyle);
var _css = require("@emotion/css");
var _adapter = require("@nitipit/adapter/src/adapter");
class ProgressBarStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            progressColor: "blue",
            trackColor: "#ccc",
            thickness: "5px",
            borderRadius: "5px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const loopAnimation = (0, _css.keyframes)`
        from {
            width: 0;
            opacity: 1;
        }
        25% {
            opacity: 1;
        }
        to {
            width: 100%;
            opacity: 0;
        }
        `;
        let css = `
        width: 100%;
        &.value {
            display: flex;
            justify-content: flex-start;
            div[el="progress"] {
                will-change: width opacity;
                transition: width 0.25s ease 0s;
                animation: none;
            }
        }

        &.loop {
            display: flex;
            justify-content: center;
            div[el="progress"] {
                will-change: width, opacity;
                transition: none;
                animation: ${loopAnimation} 1.5s ease infinite;
            }
        }

        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._progressColor(style)}
        ${this._trackColor(style)}
        ${this._thickness(style)}
        ${this._borderRadius(style)}
        `.trim();
        return css;
    }
    static _progressColor(style = {}) {
        if (style.progressColor == undefined) return "";
        return `
        div[el="progress"] {
            background-color: ${style.progressColor};
        }
        `.trim();
    }
    static _trackColor(style = {}) {
        if (style.trackColor == undefined) return "";
        return `
        background-color: ${style.trackColor};
        `.trim();
    }
    static _thickness(style = {}) {
        if (style.thickness == undefined) return "";
        return `
        div[el="progress"] {
            height: ${style.thickness};
        }
        `.trim();
    }
    static _borderRadius(style = {}) {
        if (style.borderRadius == undefined) return "";
        return `
        border-radius: ${style.borderRadius};
        div[el="progress"] {
            border-radius: ${style.borderRadius};
        }
        `.trim();
    }
}

},{"@emotion/css":"gyRZs","@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"2RkPm":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ProgressCircle", ()=>ProgressCircle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _progressCircleStyle = require("./progress-circle.style");
class ProgressCircle extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _progressCircleStyle.ProgressCircleStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    get radius() {
        return this._radius;
    }
    set radius(value) {
        this._radius = value;
        this.addStyle({
            radius: value
        });
        this.render();
    }
    get trackWidth() {
        return this._trackWidth;
    }
    set trackWidth(value) {
        this._trackWidth = value;
        this.addStyle({
            trackWidth: value
        });
        this.render();
    }
    set value(value) {
        if (typeof value != "number") value = parseFloat(value);
        this._value = value;
        if (isNaN(value)) {
            this.toLoop();
            return;
        }
        this.setProgress(value / this.max);
    }
    get value() {
        return this._value;
    }
    constructor(){
        super();
        this.max = 100;
        this.el = {
            circle1: null,
            circle2: null
        };
        this._radius = this._class.Style.default.radius;
        this._trackWidth = this._class.Style.default.trackWidth;
        this.render();
    }
    render() {
        let boxSize = 2 * (this.radius + this.trackWidth);
        let cx = this.radius + this.trackWidth;
        let cy = cx;
        (0, _uhtml.render)(this, (0, _uhtml.svg)`
        <svg viewBox=${`0 0 ${boxSize} ${boxSize}`}>
            <g>
                <circle el="circle1"
                    fill="transparent"
                    r="${this.radius}"
                    cx=${cx}
                    cy=${cy} />
                <circle el="circle2"
                    fill="transparent"
                    r="${this.radius}"
                    cx=${cx}
                    cy=${cy} />
            </g>
        </svg>
        `);
        this.el.circle1 = this.querySelector('circle[el="circle1"]');
        this.el.circle2 = this.querySelector('circle[el="circle2"]');
        this.max = parseFloat(this.getAttribute("max")) || this.max;
        this.value = parseFloat(this.getAttribute("value"));
    }
    toLoop() {
        this.classList.remove("value");
        this.classList.add("loop");
    }
    setProgress(ratio) {
        this.classList.remove("loop");
        this.classList.add("value");
        const circumference = 2 * Math.PI * this.radius;
        const offset = circumference - ratio * circumference;
        this.el.circle2.style.strokeDashoffset = offset.toString();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./progress-circle.style":"6KRvC","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"6KRvC":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ProgressCircleStyle", ()=>ProgressCircleStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _css = require("@emotion/css");
class ProgressCircleStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            radius: 75,
            trackWidth: 25,
            progressColor: "blue",
            trackColor: "#ccc"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const rotateAnimation = (0, _css.keyframes)`
            0% {
                transform: rotateZ(0deg);
            }
            100% {
                transform: rotateZ(360deg);
            }
        `;
        const css = `
        display: flex;
        overflow: hidden;
        &.loop svg {
            animation: 2s linear infinite ${rotateAnimation};
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._radius(style)}
        ${this._trackWidth(style)}
        ${this._progressColor(style)}
        ${this._trackColor(style)}
        `.trim();
        return css;
    }
    static _progressColor(style = {}) {
        if (style.progressColor == undefined) return "";
        return `
        &.loop circle[el="circle2"] {
            stroke: ${style.progressColor};
        }
        &.value circle[el="circle2"] {
            stroke: ${style.progressColor};
        }
        `.trim();
    }
    static _trackColor(style = {}) {
        if (style.trackColor == undefined) return "";
        return `
        circle[el="circle1"] {
            stroke: ${style.trackColor};
        }
        `.trim();
    }
    static _trackWidth(style = {}) {
        if (style.trackWidth == undefined) return "";
        return `
        circle[el="circle1"] {
            stroke-width: ${style.trackWidth};
        }
        &.loop circle[el="circle2"] {
            stroke-width: ${style.trackWidth};
        }
        &.value circle[el="circle2"] {
            stroke-width: ${style.trackWidth};
        }
        `.trim();
    }
    static _radius(style = {}) {
        if (style.radius == undefined) return "";
        const circumference = Math.floor(2 * Math.PI * style.radius);
        const loopAnimation = (0, _css.keyframes)`
            0%, 25% {
                stroke-dashoffset: ${Math.floor(circumference * 0.97)};
                transform: rotate(0);
            }
            
            50%, 75% {
                stroke-dashoffset: ${Math.floor(circumference * 0.25)};
                transform: rotate(45deg);
            }
            
            100% {
                stroke-dashoffset: ${Math.floor(circumference * 0.97)};
                transform: rotate(360deg);
            }
        `;
        const css = `
        &.loop circle[el="circle2"] {
            stroke-dasharray: ${circumference};
            stroke-linecap: round;
            transition: unset;
            transform: none;
            transform-origin: 50% 50%;
            animation: 1.5s ease-in-out infinite both ${loopAnimation};
        }

        &.value circle[el="circle2"] {
            stroke-linecap: unset;
            stroke-dasharray: ${circumference} ${circumference};
            transition: stroke-dashoffset 0.25s ease-in-out;
            // axis compensation
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
            animation: unset;
        }`.trim();
        return css;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","@emotion/css":"gyRZs","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"9iVgh":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Sidebar", ()=>Sidebar);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _sidebarStyle = require("./sidebar.style");
class Sidebar extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _sidebarStyle.SidebarStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    set showAt(value) {
        this._showAt = value;
        this.setAttribute("showAt", value);
        this.mediaQuery = window.matchMedia(`(min-width: ${this.showAt})`);
    }
    get showAt() {
        return this._showAt;
    }
    constructor(){
        super();
        this.el = {
            content: null,
            overlay: null
        };
        this._showAt = "1000px";
        this.showAt = this.getAttribute("showAt") || this._showAt;
        this.el.content = this.querySelector('[el="content"]') || (0, _uhtml.html)`<div el="content">`;
        this.el.overlay = this.querySelector('[el="overlay"]') || (0, _uhtml.html)`<div el="overlay">`;
        this.render();
        this.mediaChange();
        this.mediaQuery.addEventListener("change", ()=>{
            this.mediaChange();
        });
    }
    render() {
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            ${this.el.content}
            ${this.el.overlay}
        `);
        this.el.content = this.querySelector('[el="content"]');
        this.el.overlay = this.querySelector('[el="overlay"]');
        this.el.overlay.addEventListener("click", ()=>{
            this.hide();
        });
    }
    mediaChange() {
        if (this.mediaQuery.matches) this.show({
            overlay: false
        });
        else this.hide();
    }
    show({ overlay = true } = {}) {
        this.el.content.classList.add("show");
        if (overlay) this.el.overlay.classList.add("show");
    }
    hide() {
        this.el.content.classList.remove("show");
        this.el.overlay.classList.remove("show");
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./sidebar.style":"6LCyC","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"6LCyC":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "SidebarStyle", ()=>SidebarStyle);
var _style = require("../../style");
var _adapter = require("@nitipit/adapter/src/adapter");
class SidebarStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            bgColor: "#eee",
            overlayColor: "rgba(0,0,0,0.7)"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        let css = `
        position: absolute;
        top: 0;
        left: 0;
        [el="content"] {
            position: fixed;
            z-index: 101;
            height: 100%;
            min-width: 250px;
            overflow-x: hidden;
            overflow-y: auto;
            transition: transform 0.3s;
            transform: translate3d();
            transform: translateX(-100%);;
            will-change: transform;
            &.show {
                transform: translateX(0)
            }
        }
        [el="overlay"] {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 100;
            display: none;
            width: 100%;
            height: 100%;
            &.show {
                display: block;
            }
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        let css = `
        ${this._bgColor(style)}
        ${this._overlayColor(style)}
        `.trim();
        return css;
    }
    static _bgColor(style = {}) {
        if (style.bgColor == undefined) return "";
        return `
        [el="content"] {
            ${(0, _style.bgColor)(style.bgColor)}
        }
        `.trim();
    }
    static _overlayColor(style = {}) {
        if (style.overlayColor == undefined) return "";
        return `
        [el="overlay"] {
            background-color: ${style.overlayColor};
        }
        `.trim();
    }
}

},{"../../style":"72rKO","@nitipit/adapter/src/adapter":"1Fra8","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"gsIJA":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Switch", ()=>Switch);
var _adapter = require("@nitipit/adapter/src/adapter");
var _uhtml = require("uhtml");
var _switchStyle = require("./switch.style");
class Switch extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _switchStyle.SwitchStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
    constructor(){
        super();
        this.render();
    }
    render() {
        let checkbox = this.querySelector('input[type="checkbox"]') || (0, _uhtml.html)`<input type="checkbox">`;
        let label = this.querySelector('div[el="label"]') || (0, _uhtml.html)`
                <div el="label">
                    <span></span>
                    <span></span>
                </div>
            `;
        let pin = this.querySelector('div[el="pin"]') || (0, _uhtml.html)`<div el="pin"></div>`;
        (0, _uhtml.render)(this, (0, _uhtml.html)`
            ${checkbox}
            ${label}
            ${pin}
        `);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","uhtml":"if09d","./switch.style":"aIkZb","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"aIkZb":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "SwitchStyleParam", ()=>SwitchStyleParam);
parcelHelpers.export(exports, "SwitchStyle", ()=>SwitchStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class SwitchStyleParam {
}
class SwitchStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            pinColor: "#f6f5f4",
            pinRadius: "10em",
            bgColor: "#deddda",
            activeColor: "blue"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const css = `
        display: inline-flex;
        font-weight: bold;
        line-height: initial;
        width: 3.8em;
        height: 2em;
        align-items: center;
        position: relative;

        input[type="checkbox"] {
            /* Hide default HTML checkbox */
            position: absolute;
            opacity: 0;
            cursor: pointer;
            z-index: 10;
            width: 100%;
            height: 100%;
            margin: 0;
        }

        div[el="label"] {
            display: flex;
            width: 100%;
            height: 100%;
            ${(0, _style.lift)({
            level: 1
        })}
            overflow: hidden;
            transition: .4s;
            align-items: center;
            text-align: center;
            padding-left: 0.2em;
            padding-right: 0.2em;
        }

        div[el="pin"] {
            box-sizing: border-box;
            position: absolute;
            top: 50%;
            left: 0.1em;
            transform: translateY(-50%);
            text-align: center;
            width: 1.8em;
            height: 1.8em;
            border: 1px solid #9a9996;
            transition: .2s;
        }

        div[el="label"] > span {
            font-size: 0.8em;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 50%;
        }

        input[type="checkbox"]:checked ~ div[el="pin"] {
            transform: translate(1.8em, -50%);
            will-change: transform;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._pinColor(style)}
        ${this._pinRadius(style)}
        ${this._bgColor(style)}
        ${this._activeColor(style)}
        `.trim();
        return css;
    }
    static _pinColor(style = {}) {
        if (style.pinColor == undefined) return "";
        return `
        div[el="pin"] {
            ${(0, _style.bgColor)(style.pinColor)}
        }
        `.trim();
    }
    static _pinRadius(style = {}) {
        return `
        div[el="pin"] {
            border-radius: ${style.pinRadius}
        }
        div[el="label"] {
            border-radius: ${style.pinRadius}
        }
        `;
    }
    static _bgColor(style = {}) {
        if (style.bgColor == undefined) return "";
        return `
        div[el="label"] {
            ${(0, _style.bgColor)(style.bgColor)}
        }
        `.trim();
    }
    static _activeColor(style = {}) {
        if (style.activeColor == undefined) return "";
        return `
        input[type="checkbox"]:checked ~ div[el="label"] {
            ${(0, _style.bgColor)(style.activeColor)}
        }
        `.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"8Zzpz":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Tab", ()=>Tab);
var _adapter = require("@nitipit/adapter/src/adapter");
var _tabStyle = require("./tab.style");
class Tab extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _tabStyle.TabStyle);
    })();
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    constructor(){
        super();
        this.setupTab();
    }
    setupTab() {
        for (let tab of this.querySelectorAll("div")){
            if (tab.parentNode != this) break;
            if (tab.classList.contains("active")) this.activedTab = tab;
            tab.addEventListener("click", (event)=>{
                this.activateTab(event.target);
            });
        }
    }
    activateTab(tab) {
        try {
            this.activedTab.classList.remove("active");
        } catch (err) {}
        tab.classList.add("active");
        this.activedTab = tab;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./tab.style":"ekIed","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"ekIed":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TabStyle", ()=>TabStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
class TabStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            tabColor: "#ccc",
            hoverColor: "#ddd",
            activeColor: "blue",
            separatorLineColor: "black",
            separatorLineWidth: "1px"
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const css = `
        display: inline-flex;
        flex-wrap: wrap;
        overflow: hidden;
        border-radius: 4px;
        > div {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            padding: 0.25em 0.5em 0.25em 0.5em;
            line-height: 1;
            height: 1.8em;
        }
        > div:not(:last-of-type) {
            border-right-style: solid;
        }
        > div.active {
            ${(0, _style.lift)({
            level: 2
        })}
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._tabColor(style)}
        ${this._hoverColor(style)}
        ${this._activeColor(style)}
        ${this._separatorLineColor(style)}
        ${this._separatorLineWidth(style)}
        `.trim();
        return css;
    }
    static _tabColor(style = {}) {
        if (style.tabColor == undefined) return "";
        return `
        ${(0, _style.bgColor)(style.tabColor)}
        `.trim();
    }
    static _hoverColor(style = {}) {
        if (style.hoverColor == undefined) return "";
        return `
        > div:hover {
            ${(0, _style.bgColor)(style.hoverColor)}
        }`.trim();
    }
    static _activeColor(style = {}) {
        if (style.activeColor == undefined) return "";
        return `
        > div.active {
            ${(0, _style.bgColor)(style.activeColor)}
        }`.trim();
    }
    static _separatorLineColor(style = {}) {
        if (style.separatorLineColor == undefined) return "";
        return `
        border-color: ${style.separatorLineColor};
        > div:not(:last-of-type) {
            border-right-color: ${style.separatorLineColor};
        }`.trim();
    }
    static _separatorLineWidth(style = {}) {
        if (style.separatorLineWidth == undefined) return "";
        return `
        border-width: ${style.separatorLineWidth};
        > div:not(:last-of-type) {
            border-right-width: ${style.separatorLineWidth};
        }`.trim();
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"5egmO":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "Table", ()=>Table);
var _adapter = require("@nitipit/adapter/src/adapter");
var _tableStyle = require("./table.style");
class Table extends (0, _adapter.Adapter) {
    static #_ = (()=>{
        this.Style = (0, _tableStyle.TableStyle);
    })();
    static #_1 = (()=>{
        this.tagName = "table";
    })();
    static define(tagName) {
        if (tagName.toLowerCase() === "table") {
            this.tagName = tagName;
            this.initStyle();
            return;
        }
        super.define(tagName);
    }
    static tagStyle(style) {
        super.tagStyle(style);
    }
    static classStyle(class_, style) {
        super.classStyle(class_, style);
    }
    addStyle(style) {
        super.addStyle(style);
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","./table.style":"f4j6f","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"f4j6f":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TableStyle", ()=>TableStyle);
var _adapter = require("@nitipit/adapter/src/adapter");
var _style = require("../../style");
const Color = require("cd24947c88618007");
class TableStyle extends (0, _adapter.StyleClass) {
    static #_ = (()=>{
        this.default = {
            theadBgColor: "#ccc",
            activeColor: "blue",
            horizontalLine: true,
            verticalLine: true
        };
    })();
    static css(style = {}) {
        style = {
            ...this.default,
            ...style
        };
        const css = `
        display: block;
        overflow: auto;
        border: 1px solid;
        border-collapse: separate;
        border-spacing: 0;

        thead {
            font-weight: bold;
        }
        th, td {
            padding: 0.5rem;
        }
        ${this.style(style)}
        `.trim();
        return css;
    }
    static style(style = {}) {
        const css = `
        ${this._theadBgColor(style)}
        ${this._activeColor(style)}
        ${this._horizontalLine(style)}
        ${this._verticalLine(style)}
        `.trim();
        return css;
    }
    static _theadBgColor(style = {}) {
        if (style.theadBgColor == undefined) return "";
        return `
        thead {
            ${(0, _style.bgColor)(style.theadBgColor)}
        }`.trim();
    }
    static _activeColor(style = {}) {
        if (style.activeColor == undefined) return "";
        return `
        tbody td:hover {
            ${(0, _style.bgColor)(style.activeColor)}
            &::selection {
                ${(0, _style.bgColor)(Color(style.activeColor).rotate(180))}
            }
        }
        `.trim();
    }
    static _horizontalLine(style = {}) {
        if (style.horizontalLine == undefined) return "";
        let horizontalLineCSS = null;
        if (style.horizontalLine) horizontalLineCSS = `
            td, th {
                border-bottom: 1px solid;
            }
            thead {
                td, th {
                    border-bottom: 3px double;
                }
            }`.trim();
        else horizontalLineCSS = `
            td, th {
                border-bottom: 0;
            }
            thead {
                td, th {
                    border-bottom: 0;
                }
            }`.trim();
        return horizontalLineCSS;
    }
    static _verticalLine(style = {}) {
        if (style.verticalLine == undefined) return;
        let verticalLineCSS = null;
        if (style.verticalLine) verticalLineCSS = `
            td:not(:first-child), th:not(:first-child) {
                border-left: 1px solid;
            }`.trim();
        else verticalLineCSS = `
            td:not(:first-child), th:not(:first-child) {
                border-left: 0;
            }`.trim();
        return verticalLineCSS;
    }
}

},{"@nitipit/adapter/src/adapter":"1Fra8","../../style":"72rKO","cd24947c88618007":"gW2oi","@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}],"lFBda":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "theme", ()=>theme);
parcelHelpers.export(exports, "palette", ()=>palette);
const theme = {
    "light-pink": "#f7b2b7",
    "ultra-red": "#f7717d",
    "china-pink": "#de639a",
    "maximum-purple": "#7f2982",
    "dark-purple": "#16001e"
};
const palette = {
    "blue": "#3584e4",
    "green": "#33d17a",
    "yellow": "#f6d32d",
    "orange": "#ff7800",
    "red": "#e01b24",
    "purple": "#9141ac",
    "brown": "#986a44",
    "light": "#deddda",
    "dark": "#3d3846"
};

},{"@parcel/transformer-js/src/esmodule-helpers.js":"gkKU3"}]},["ek91E","3UFPP"], "3UFPP", "parcelRequire94c2")

//# sourceMappingURL=sidebar.js.map
