(function () {
    function urlBase64ToUint8Array(base64String) {
        const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
        const rawData = atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; i += 1) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async function fetchJson(url, options) {
        const opts = Object.assign({}, options || {});
        opts.headers = Object.assign({}, opts.headers || {});
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
        if (csrfToken) {
            opts.headers["X-CSRF-Token"] = csrfToken;
        }
        const resp = await fetch(url, opts);
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.ok) {
            let msg = data.error || `HTTP ${resp.status}`;
            if (msg === "push_not_configured") {
                const d = data.detail || {};
                msg = `Push no configurado. detalle: lib=${!!d.push_disponible}, pub=${!!d.public_key_valida}, priv=${!!d.private_key_present}, py=${d.python_executable || "-"}`;
            }
            throw new Error(msg);
        }
        return data;
    }

    function showStatus(el, text, ok) {
        el.className = ok ? "alert alert-success mt-2 mb-0" : "alert alert-warning mt-2 mb-0";
        el.textContent = text;
        el.hidden = false;
    }

    async function enablePush(statusEl) {
        if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
            throw new Error("Este navegador no soporta notificaciones push.");
        }

        const keyData = await fetchJson("/notificaciones/push/public_key");
        const appServerKey = urlBase64ToUint8Array(keyData.public_key);
        const registration = await navigator.serviceWorker.register("/static/js/sw.js");
        let subscription = await registration.pushManager.getSubscription();
        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: appServerKey,
            });
        }

        await fetchJson("/notificaciones/push/subscribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subscription }),
        });

        showStatus(statusEl, "Push activado correctamente en este navegador.", true);
    }

    document.addEventListener("DOMContentLoaded", () => {
        const enableBtn = document.getElementById("push-enable-btn");
        const statusEl = document.getElementById("push-status");
        if (!enableBtn || !statusEl) {
            return;
        }

        enableBtn.addEventListener("click", async () => {
            enableBtn.disabled = true;
            try {
                await enablePush(statusEl);
            } catch (err) {
                showStatus(statusEl, `No se pudo activar push: ${err.message}`, false);
            } finally {
                enableBtn.disabled = false;
            }
        });
    });
})();
