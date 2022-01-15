import type { Writable, Updater, Subscriber, Unsubscriber } from 'svelte/store';
import type Backbone from 'backbone';
import { DOMWidgetModel } from "@jupyter-widgets/base";


/**
 * Creates a Svelte-Store out of a backbone model attribute.
 *
 * @param model The backbone model this to attach
 * @param name  The name of the attribute to watch.
 */
export function model_attribute<T>(model: Backbone.Model, name: string): Writable<T> {
    return {
        // Just set the value
        set(value: T) {
            model.set(name, value);
            if (model instanceof DOMWidgetModel)
                model.save_changes();
        },

        // Change the value.
        update(updater: Updater<T>) {
            model.set(name, updater(model.get(name)));
        },

        // Subscribe to changes to the value.
        subscribe(subscriber: Subscriber<T>): Unsubscriber {
            // Create our own function instance to make sure
            // one can remove it again with the Unsubscriber.
            const cb = (_: any, value: T) => {
                subscriber(value);
            };
            model.on(`change:${name}`, cb);
            subscriber(model.get(name));
            return () => {
                model.off(`change:${name}`, cb);
            };
        }
    };
}


export function debounce<T>(time: number, parent: Writable<T>) {
    let currentId: any = -1;
    return {
        set(value: T) {
            if (currentId != -1) clearTimeout(currentId);
            currentId = setTimeout(() => {
                currentId = -1;
                parent.set(value);
            }, time);
        },

        update(update: Updater<T>) {
            parent.update(update);
        },

        subscribe(subscriber: Subscriber<T>): Unsubscriber {
            return parent.subscribe(subscriber);
        }
    }
}
