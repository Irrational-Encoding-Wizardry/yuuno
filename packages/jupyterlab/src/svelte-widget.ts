import { DOMWidgetView, WidgetModel } from '@jupyter-widgets/base';
import type { SvelteComponentTyped } from 'svelte/types/runtime';


/**
 * Simple Wrapper-Type for Svelte Components.
 */
export abstract class SvelteWidgetView<T extends SvelteComponentTyped> extends DOMWidgetView {
    private component: T|null = null;

    /**
     * Override this function to build a new svelte widget.
     */
    protected abstract buildComponent(): T;

    /**
     * Destroys a svelte component.
     */
    private _destroyComponent() {
        if (this.component !== null) {
            this.component.$destroy();
            this.component = null;
        }
    }

    /**
     * Renders the svelte component.
     *
     * Svelte will subscribe to model changes it cares about by itself.
     */
    render() {
        this._destroyComponent();
        this.component = this.buildComponent();
    }


    /**
     * Unmounts a svelte component.
     */
    remove() {
        this._destroyComponent();
        return super.remove();
    }
}


export type SimpleSvelteConstructor<T extends SvelteComponentTyped> = new (options: {target: HTMLElement, props: { component: WidgetModel }}) => T;

/**
 * Creates a new class for a specific widget.
 */
export function widgetFor<T extends SvelteComponentTyped>(c: SimpleSvelteConstructor<T>): typeof DOMWidgetView {
    return class SvelteWidgetImpl extends SvelteWidgetView<T> {
        protected buildComponent(): T {
            return new c({
                target: this.el,
                props: { component: this.model }
            });
        }
    }
}
