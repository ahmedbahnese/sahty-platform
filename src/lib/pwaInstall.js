// Shared install-state for the Sahty PWA.
//
// Single capture point for `beforeinstallprompt` / `appinstalled`.
// The browser fires `beforeinstallprompt` once per page load; capturing it
// here (module level, bound once) keeps every consumer — the navbar button,
// the install modal, the first-visit banner and the Emergency page — reading
// the same one-shot event. `window.__sahtyInstallPrompt` stays in sync so
// the older helpers in `lib/push.js` (getInstallPromptEvent) keep working.

import { useEffect, useState } from 'react'

const listeners = new Set()

let promptEvent = typeof window !== 'undefined' ? window.__sahtyInstallPrompt || null : null
let installed = false

function snapshot() {
  return { promptEvent, installed }
}

function emit() {
  const state = snapshot()
  listeners.forEach(listener => listener(state))
}

function onPrompt(event) {
  event.preventDefault()
  promptEvent = event
  window.__sahtyInstallPrompt = event
  emit()
}

function onInstalled() {
  installed = true
  promptEvent = null
  window.__sahtyInstallPrompt = null
  emit()
}

function bindOnce() {
  if (typeof window === 'undefined') return
  if (window.__sahtyPwaInstallBound) {
    // Adopt an event captured before this module loaded, so nothing is lost.
    if (window.__sahtyInstallPrompt && !promptEvent) {
      promptEvent = window.__sahtyInstallPrompt
    }
    return
  }
  window.__sahtyPwaInstallBound = true
  if (window.__sahtyInstallPrompt) promptEvent = window.__sahtyInstallPrompt
  installed =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  window.addEventListener('beforeinstallprompt', onPrompt)
  window.addEventListener('appinstalled', onInstalled)
}

bindOnce()

export function usePwaInstall() {
  const [state, setState] = useState(snapshot)
  useEffect(() => {
    bindOnce()
    const listener = next => setState(next)
    listeners.add(listener)
    // Re-sync in case the event arrived before this component mounted.
    setState(snapshot())
    return () => listeners.delete(listener)
  }, [])
  const isIOS =
    typeof window !== 'undefined' && /iphone|ipad|ipod/i.test(window.navigator.userAgent)
  return {
    promptEvent: state.promptEvent,
    installed: state.installed,
    canPrompt: Boolean(state.promptEvent) && !state.installed,
    isIOS,
  }
}

// Show the browser's native install prompt. Returns 'accepted' | 'dismissed'
// | 'unavailable'. The prompt event is one-shot: it is cleared after use
// whether the user accepted or declined, so a declined install can be
// retried later only when the browser offers the prompt again.
export async function promptInstall() {
  const event =
    promptEvent || (typeof window !== 'undefined' ? window.__sahtyInstallPrompt : null)
  if (!event) return 'unavailable'
  try {
    event.prompt()
    const choice = await event.userChoice.catch(() => null)
    const outcome = choice && choice.outcome === 'accepted' ? 'accepted' : 'dismissed'
    if (outcome === 'accepted') {
      installed = true
    }
    promptEvent = null
    if (typeof window !== 'undefined') window.__sahtyInstallPrompt = null
    emit()
    return outcome
  } catch (_) {
    promptEvent = null
    if (typeof window !== 'undefined') window.__sahtyInstallPrompt = null
    emit()
    return 'unavailable'
  }
}

// Browser family, used ONLY to pick the right manual-install instructions
// text. Capability detection (canPrompt / installed / isIOS) always decides
// first; the family never decides whether installation is possible.
export function getBrowserFamily() {
  if (typeof window === 'undefined') return 'other'
  const ua = window.navigator.userAgent || ''
  if (/edg/i.test(ua)) return 'edge'
  if (/firefox|fxios/i.test(ua)) return 'firefox'
  if (/iphone|ipad|ipod/i.test(ua)) return 'safari'
  if (/chrome|crios/i.test(ua)) return 'chrome'
  if (/safari/i.test(ua)) return 'safari'
  return 'other'
}
