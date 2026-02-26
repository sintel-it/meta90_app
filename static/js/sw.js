self.addEventListener("push", (event) => {
    let data = {};
    try {
        data = event.data ? event.data.json() : {};
    } catch (e) {
        data = {};
    }

    const title = data.title || "Meta Inteligente";
    const options = {
        body: data.body || "Tienes una nueva notificacion.",
        data: { url: data.url || "/notificaciones" },
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    const targetUrl = (event.notification.data && event.notification.data.url) || "/notificaciones";
    event.waitUntil(clients.openWindow(targetUrl));
});

