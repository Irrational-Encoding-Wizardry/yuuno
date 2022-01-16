/**
 * Defines a new module.
 */
export function define(name: string, func: () => any) {
    (window as any).define(name, func);
}
