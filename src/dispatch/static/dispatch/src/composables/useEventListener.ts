import { onMounted, onUnmounted } from "vue"

/**
 * A composable function to handle event listeners.
 *
 * @param target - The target to attach the event listener to.
 * @param event - The event to listen for.
 * @param callback - A function to call when the event is triggered.
 *
 * Usage:
 * ```
 * import { useEventListener } from '@/composables/useEventListener'
 *
 * // In your setup function, call useEventListener with your target, event, and callback function
 * // Example for listening to 'mousemove' event on window
 * useEventListener(window, 'mousemove', (event) => {
 *   // Do something when 'mousemove' event is triggered
 * })
 * ```
 */
export function useEventListener(target: Window, event: string, callback: (e: Event) => void) {
  // On component mount, add the event listener to the target
  onMounted(() => target.addEventListener(event, callback))

  // On component unmount, remove the event listener from the target
  onUnmounted(() => target.removeEventListener(event, callback))
}
