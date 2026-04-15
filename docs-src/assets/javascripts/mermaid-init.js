document.addEventListener("DOMContentLoaded", () => {
  const mermaidBlocks = document.querySelectorAll("pre.mermaid");

  if (!window.mermaid || mermaidBlocks.length === 0) {
    return;
  }

  for (const pre of mermaidBlocks) {
    if (pre.dataset.mermaidProcessed === "true") {
      continue;
    }

    const container = document.createElement("div");
    container.className = "mermaid";
    container.textContent = pre.textContent ?? "";
    pre.dataset.mermaidProcessed = "true";
    pre.replaceWith(container);
  }

  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
  });
  window.mermaid.run({
    querySelector: ".mermaid",
  });
});
