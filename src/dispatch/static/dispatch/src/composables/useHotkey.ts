import { Ref, ref } from "vue"
import { useEventListener } from "@/composables/useEventListener"

type Key = keyof typeof KeyboardEvent.prototype

/**
 * A composable function to handle hotkeys.
 *
 * @param keyCombination - An array of keys that form the hotkey.
 * @param callback - A function to call when the hotkey is pressed.
 *
 * Usage:
 * ```
 * import { useHotKey } from './useHotKey'
 *
 * // In your setup function, call useHotKey with your desired key combination and callback function
 * // Example for single key 'a'
 * useHotKey(["a"], (event) => {
 *   // Do something when 'a' is pressed
 * })
 *
 * // Example for combination of keys 'Meta' + 'Shift' + 'p'
 * useHotKey(["Meta", "Shift", "p"], (event) => {
 *   // Do something when 'Meta' + 'Shift' + 'p' is pressed
 * })
 * ```
 */
export function useHotKey(keyCombination: Key[], callback: (event: KeyboardEvent) => void) {
  // Define a ref to keep track of keys that are currently pressed
  // This is a record where the keys are Key types and the values are booleans
  let keysPressed: Ref<Record<Key, boolean>> = ref({} as Record<Key, boolean>)

  const handleKeyDown = (event: KeyboardEvent) => {
    // When a key is pressed, add it to the keysPressed record
    keysPressed.value[event.key] = true

    // Check if all keys in the keyCombination array are currently pressed
    // and that the last key pressed is the final key in the keyCombination array
    // If so, call the provided callback function
    if (
      keyCombination.every((key) => keysPressed.value[key]) &&
      event.key === keyCombination[keyCombination.length - 1]
    ) {
      callback(event)
    }
  }

  const handleKeyUp = (event: KeyboardEvent) => {
    // When a key is released, remove it from the keysPressed record
    delete keysPressed.value[event.key]
  }

  useEventListener(window, "keydown", handleKeyDown)
  useEventListener(window, "keyup", handleKeyUp)
}
