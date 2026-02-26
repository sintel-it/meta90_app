(function () {
    const STORAGE_KEY = "meta90_accounts";

    function readAccounts() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const arr = raw ? JSON.parse(raw) : [];
            if (!Array.isArray(arr)) return [];
            return arr.map((x) => String(x || "").trim()).filter(Boolean);
        } catch (_) {
            return [];
        }
    }

    function writeAccounts(accounts) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(accounts.slice(0, 10)));
    }

    function upsertAccount(username) {
        const current = String(username || "").trim();
        if (!current) return;
        const arr = readAccounts().filter((x) => x.toLowerCase() !== current.toLowerCase());
        arr.unshift(current);
        writeAccounts(arr);
    }

    function renderList() {
        const list = document.getElementById("account-switcher-list");
        if (!list) return;
        const active = String(list.dataset.activeUser || "").trim();
        const accounts = readAccounts();

        if (!accounts.length) {
            list.innerHTML = '<div class="small soft-text px-2 py-1">No hay cuentas guardadas aun.</div>';
            return;
        }

        list.innerHTML = accounts
            .map((user) => {
                const activeMark = active.toLowerCase() === user.toLowerCase() ? "&#10003;" : "";
                return (
                    '<a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"' +
                    ' href="/logout?switch_user=' + encodeURIComponent(user) + '">' +
                    '<span>' + user + "</span>" +
                    '<span class="text-success fw-bold">' + activeMark + "</span>" +
                    "</a>"
                );
            })
            .join("");
    }

    document.addEventListener("DOMContentLoaded", function () {
        const currentUserEl = document.getElementById("current-session-user");
        if (currentUserEl) {
            upsertAccount(currentUserEl.dataset.username || "");
        }
        renderList();
    });
})();
