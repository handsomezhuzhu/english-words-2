document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/login";
        return;
    }

    const headers = {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };

    loadUsers();
    loadConfig();

    async function loadUsers() {
        try {
            const res = await fetch("/admin/users", { headers });
            if (!res.ok) throw new Error("Failed to load users");
            const users = await res.json();
            const tbody = document.querySelector("#users-table tbody");
            tbody.innerHTML = "";
            users.forEach(user => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.email}</td>
                    <td>${user.is_admin ? "Yes" : "No"}</td>
                    <td>
                        <button class="btn danger small" onclick="deleteUser(${user.id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (e) {
            console.error(e);
        }
    }

    async function loadConfig() {
        try {
            const res = await fetch("/admin/ai-config", { headers });
            if (!res.ok) return; // Maybe no config yet
            const config = await res.json();
            const form = document.getElementById("ai-config-form");
            if (config.provider) form.provider.value = config.provider;
            if (config.api_key) form.api_key.value = config.api_key;
            if (config.model) form.model.value = config.model;
            if (config.temperature) form.temperature.value = config.temperature;
        } catch (e) {
            console.error(e);
        }
    }

    const configForm = document.getElementById("ai-config-form");
    if (configForm) {
        configForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(configForm);
            const payload = {
                provider: formData.get("provider"),
                api_key: formData.get("api_key"),
                model: formData.get("model"),
                temperature: Number(formData.get("temperature"))
            };

            const res = await fetch("/admin/ai-config", {
                method: "PUT",
                headers,
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert("Saved!");
            } else {
                alert("Failed to save config");
            }
        });
    }

    window.deleteUser = async (id) => {
        if (!confirm("Are you sure?")) return;
        await fetch(`/admin/users/${id}`, {
            method: "DELETE",
            headers
        });
        loadUsers();
    };
});