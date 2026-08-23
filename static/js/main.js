const colourSchemeSelect = document.querySelector("#colour-scheme");

const initialValue = localStorage.getItem("colour-scheme");

if (initialValue) {
  document.documentElement.setAttribute("data-theme", initialValue);
}

if (colourSchemeSelect) {
  if (initialValue) {
    colourSchemeSelect.value = initialValue;
  }
  colourSchemeSelect.addEventListener("input", ({ target }) => {
    switch (target.value) {
      case "light":
      case "dark":
        document.documentElement.setAttribute("data-theme", target.value);
        localStorage.setItem("colour-scheme", target.value);
        break;
      default:
        document.documentElement.removeAttribute("data-theme");
        localStorage.removeItem("colour-scheme");
    }
  });
}
