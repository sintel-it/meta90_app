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

    function initials(username) {
        const u = String(username || "").trim();
        if (!u) return "?";
        return u.slice(0, 1).toUpperCase();
    }

    function render() {
        const chooser = document.getElementById("login-account-chooser");
        const list = document.getElementById("login-account-list");
        const usernameInput = document.getElementById("login-username");
        const passwordInput = document.getElementById("login-password");
        const rememberCheck = document.getElementById("recordar_sesion");
        if (!chooser || !list || !usernameInput || !passwordInput || !rememberCheck) return;

        const selected = String(usernameInput.value || "").trim().toLowerCase();
        const accounts = readAccounts();

        if (!accounts.length) {
            chooser.hidden = false;
            list.innerHTML = '<div class="small soft-text px-2 py-1">No hay cuentas guardadas aun.</div>';
            return;
        }

        chooser.hidden = false;
        list.innerHTML = accounts
            .map((user) => {
                const active = selected && selected === user.toLowerCase();
                return (
                    '<button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center js-account-pick" data-user="' +
                    user.replace(/"/g, "&quot;") +
                    '">' +
                    '<span class="d-flex align-items-center gap-2">' +
                    '<span class="message-avatar" style="width:30px;height:30px;font-size:0.8rem;">' + initials(user) + "</span>" +
                    "<span>" + user + "</span>" +
                    "</span>" +
                    '<span class="text-success fw-bold">' + (active ? "&#10003;" : "") + "</span>" +
                    "</button>"
                );
            })
            .join("");

        list.querySelectorAll(".js-account-pick").forEach((btn) => {
            btn.addEventListener("click", () => {
                usernameInput.value = btn.dataset.user || "";
                rememberCheck.checked = true;
                passwordInput.focus();
                render();
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        const addBtn = document.getElementById("login-add-account");
        const closeBtn = document.getElementById("login-account-close");
        const usernameInput = document.getElementById("login-username");
        const form = document.getElementById("login-form");

        render();

        if (addBtn && usernameInput) {
            addBtn.addEventListener("click", () => {
                window.location.href = "/logout?clear_remember=1";
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                const chooser = document.getElementById("login-account-chooser");
                if (chooser) chooser.hidden = true;
            });
        }

        if (form && usernameInput) {
            form.addEventListener("submit", () => {
                const user = String(usernameInput.value || "").trim();
                if (!user) return;
                const arr = readAccounts().filter((x) => x.toLowerCase() !== user.toLowerCase());
                arr.unshift(user);
                writeAccounts(arr);
            });
        }
    });
})();
