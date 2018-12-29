export function createMountedElement(target, ...args) {
    const el = document.createElement(...args);
    target.appendChild(el);
    return el;
}

export function emptyElement(target) {
    while (target.firstChild)
        target.removeChild(target.firstChild);
}