'use strict';

let components = document.querySelector(".components-block");

if (components.childElementCount == 0) {
  components.style.boxShadow = 'none';
  let div = document.createElement("div")
  div.className = "text-warning";
  div.innerHTML = "There are no items created yet. Be the first one!"
  components.appendChild(div)
}
