const API_BASE = "";

// DOM elements
const productsTableBody = document.querySelector("#products-table tbody");
const messageBox = document.getElementById("message");
const btnAdd = document.getElementById("btn-add");
const modal = document.getElementById("product-form-modal");
const formTitle = document.getElementById("form-title");
const productForm = document.getElementById("product-form");
const btnCancel = document.getElementById("btn-cancel");

const navProducts = document.getElementById("nav-products");
const navWorkshops = document.getElementById("nav-workshops");
const pageProducts = document.getElementById("page-products");
const pageWorkshops = document.getElementById("page-workshops");

const workshopsProductSelect = document.getElementById("workshops_product_select");
const btnLoadWorkshops = document.getElementById("btn-load-workshops");
const workshopsTableBody = document.querySelector("#workshops-table tbody");
const workshopsMessage = document.getElementById("workshops-message");
const productionTimeBox = document.getElementById("production-time");

const rawForm = document.getElementById("raw-form");
const rawResult = document.getElementById("raw-result");

// Navigation
navProducts.addEventListener("click", () => {
    navProducts.classList.add("active");
    navWorkshops.classList.remove("active");
    pageProducts.classList.add("visible");
    pageWorkshops.classList.remove("visible");
});

navWorkshops.addEventListener("click", () => {
    navWorkshops.classList.add("active");
    navProducts.classList.remove("active");
    pageWorkshops.classList.add("visible");
    pageProducts.classList.remove("visible");
});

// Helpers
function showMessage(element, text, type = "info") {
    element.textContent = text;
    element.classList.remove("hidden", "error", "info");
    element.classList.add(type);
}

function hideMessage(element) {
    element.classList.add("hidden");
}

// Load dictionaries
async function loadProductTypes(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">-- Выберите --</option>';
    const res = await fetch(`${API_BASE}/product-types`);
    if (!res.ok) return;
    const data = await res.json();
    data.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.product_type_name;
        opt.textContent = t.product_type_name;
        select.appendChild(opt);
    });
}

async function loadMaterials(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">-- Выберите --</option>';
    const res = await fetch(`${API_BASE}/materials`);
    if (!res.ok) return;
    const data = await res.json();
    data.forEach((m) => {
        const opt = document.createElement("option");
        opt.value = m.material_name;
        opt.textContent = m.material_name;
        select.appendChild(opt);
    });
}

// Products
async function loadProducts() {
    productsTableBody.innerHTML = "";
    hideMessage(messageBox);
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (!res.ok) throw new Error("Не удалось загрузить список продукции");
        const data = await res.json();

        if (data.length === 0) {
            productsTableBody.innerHTML = "<tr><td colspan='8' style='text-align:center'>Нет данных</td></tr>";
        }

        data.forEach((p) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${p.product_id}</td>
                <td>${p.product_name}</td>
                <td>${p.article}</td>
                <td>${p.min_partner_cost.toFixed(2)}</td>
                <td>${p.product_type_name ?? ""}</td>
                <td>${p.main_material_name ?? ""}</td>
                <td>${p.total_production_time} ч</td>
                <td>
                    <button class="secondary btn-edit" data-id="${p.product_id}">✏️</button>
                    <button class="secondary btn-delete" data-id="${p.product_id}">🗑️</button>
                </td>
            `;
            productsTableBody.appendChild(tr);
        });

        document.querySelectorAll(".btn-edit").forEach((btn) =>
            btn.addEventListener("click", () => openEditProduct(btn.dataset.id))
        );
        document.querySelectorAll(".btn-delete").forEach((btn) =>
            btn.addEventListener("click", () => deleteProduct(btn.dataset.id))
        );

        updateWorkshopsProductSelect(data);
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
}

function updateWorkshopsProductSelect(products) {
    workshopsProductSelect.innerHTML = '<option value="">-- Выберите продукт --</option>';
    products.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.product_id;
        opt.textContent = `${p.product_id} — ${p.product_name}`;
        workshopsProductSelect.appendChild(opt);
    });
}

btnAdd.addEventListener("click", () => {
    formTitle.textContent = "Добавить продукт";
    productForm.reset();
    document.getElementById("product_id").value = "";
    loadProductTypes("product_type_name");
    loadMaterials("main_material_name");
    modal.classList.remove("hidden");
});

btnCancel.addEventListener("click", () => {
    modal.classList.add("hidden");
});

modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
});

async function openEditProduct(id) {
    hideMessage(messageBox);
    const res = await fetch(`${API_BASE}/products`);
    if (!res.ok) {
        showMessage(messageBox, "Не удалось получить данные", "error");
        return;
    }
    const data = await res.json();
    const p = data.find((x) => x.product_id === Number(id));
    if (!p) {
        showMessage(messageBox, "Продукт не найден", "error");
        return;
    }

    formTitle.textContent = "Редактировать продукт";
    document.getElementById("product_id").value = p.product_id;
    document.getElementById("product_name").value = p.product_name;
    document.getElementById("article").value = p.article;
    document.getElementById("min_partner_cost").value = p.min_partner_cost;

    await loadProductTypes("product_type_name");
    await loadMaterials("main_material_name");
    if (p.product_type_name) document.getElementById("product_type_name").value = p.product_type_name;
    if (p.main_material_name) document.getElementById("main_material_name").value = p.main_material_name;

    modal.classList.remove("hidden");
}

productForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessage(messageBox);

    const id = document.getElementById("product_id").value;
    const product_name = document.getElementById("product_name").value.trim();
    const article = Number(document.getElementById("article").value);
    const min_partner_cost = Number(document.getElementById("min_partner_cost").value);
    const product_type_name = document.getElementById("product_type_name").value.trim() || null;
    const main_material_name = document.getElementById("main_material_name").value.trim() || null;

    if (!product_name) return showMessage(messageBox, "Введите наименование", "error");
    if (isNaN(article) || article < 0) return showMessage(messageBox, "Артикул ≥ 0", "error");
    if (isNaN(min_partner_cost) || min_partner_cost < 0) return showMessage(messageBox, "Стоимость ≥ 0", "error");

    const payload = { product_name, article, min_partner_cost: +min_partner_cost.toFixed(2), product_type_name, main_material_name };

    try {
        let res;
        if (id) {
            res = await fetch(`${API_BASE}/products/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
        } else {
            res = await fetch(`${API_BASE}/products`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Ошибка сохранения");
        }
        modal.classList.add("hidden");
        await loadProducts();
        showMessage(messageBox, "Сохранено", "info");
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
});

async function deleteProduct(id) {
    if (!confirm("Удалить продукт?")) return;
    try {
        const res = await fetch(`${API_BASE}/products/${id}`, { method: "DELETE" });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Ошибка удаления");
        }
        await loadProducts();
        showMessage(messageBox, "Удалено", "info");
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
}

// Workshops
btnLoadWorkshops.addEventListener("click", async () => {
    hideMessage(workshopsMessage);
    workshopsTableBody.innerHTML = "";
    productionTimeBox.textContent = "";

    const productId = Number(workshopsProductSelect.value);
    if (!productId) {
        showMessage(workshopsMessage, "Выберите продукт", "error");
        return;
    }
    try {
        const resWs = await fetch(`${API_BASE}/products/${productId}/workshops`);
        if (!resWs.ok) throw new Error("Не удалось загрузить цеха");
        const wsData = await resWs.json();
        if (wsData.length === 0) {
            workshopsTableBody.innerHTML = "<tr><td colspan='4' style='text-align:center'>Нет данных</td></tr>";
        } else {
            wsData.forEach((w) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${w.workshop_name}</td>
                    <td>${w.workshop_type}</td>
                    <td>${w.num_employees}</td>
                    <td>${w.time_in_workshop} ч</td>
                `;
                workshopsTableBody.appendChild(tr);
            });
        }

        const resTime = await fetch(`${API_BASE}/products/${productId}/production_time`);
        if (resTime.ok) {
            const t = await resTime.json();
            productionTimeBox.textContent = `Общее время изготовления: ${t.total_production_time} ч`;
        }
    } catch (e) {
        showMessage(workshopsMessage, e.message, "error");
    }
});

// Raw material calculation
rawForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    rawResult.textContent = "";

    const product_type_name = document.getElementById("raw_product_type_name").value.trim();
    const material_name = document.getElementById("raw_material_name").value.trim();
    const quantity = Number(document.getElementById("raw_quantity").value);
    const param1 = Number(document.getElementById("raw_param1").value);
    const param2 = Number(document.getElementById("raw_param2").value);

    if (!product_type_name || !material_name) {
        rawResult.textContent = "Выберите тип и материал";
        return;
    }
    if (isNaN(quantity) || quantity < 0 || isNaN(param1) || param1 <= 0 || isNaN(param2) || param2 <= 0) {
        rawResult.textContent = "Проверьте введённые значения";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/calculate_raw_material`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_type_name, material_name, quantity, param1, param2 }),
        });
        if (!res.ok) throw new Error("Ошибка расчёта");
        const data = await res.json();
        if (data.required_raw_material === -1) {
            rawResult.textContent = "Ошибка данных (тип/материал не найден)";
        } else {
            rawResult.textContent = `Необходимое количество сырья: ${data.required_raw_material}`;
        }
    } catch (e) {
        rawResult.textContent = e.message;
    }
});

// Initial load
async function init() {
    await loadProducts();
    await loadProductTypes("raw_product_type_name");
    await loadMaterials("raw_material_name");
    await loadProductTypes("product_type_name");
    await loadMaterials("main_material_name");
}

init();

