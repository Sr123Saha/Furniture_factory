const API_BASE = "";

const productsTableBody = document.querySelector("#products-table tbody");
const messageBox = document.getElementById("message");
const btnAdd = document.getElementById("btn-add");
const modal = document.getElementById("product-form-modal");
const formTitle = document.getElementById("form-title");
const productForm = document.getElementById("product-form");
const btnCancel = document.getElementById("btn-cancel");

const navButtons = {
    products: document.getElementById("nav-products"),
    productTypes: document.getElementById("nav-product-types"),
    materials: document.getElementById("nav-materials"),
    workshops: document.getElementById("nav-workshops"),
    productWorkshops: document.getElementById("nav-product-workshops"),
    calc: document.getElementById("nav-calc")
};

const pages = {
    products: document.getElementById("page-products"),
    productTypes: document.getElementById("page-product-types"),
    materials: document.getElementById("page-materials"),
    workshops: document.getElementById("page-workshops"),
    productWorkshops: document.getElementById("page-product-workshops"),
    calc: document.getElementById("page-calc")
};

const productTypesTableBody = document.querySelector("#product-types-table tbody");
const materialsTableBody = document.querySelector("#materials-table tbody");
const workshopsTableBody = document.querySelector("#workshops-table tbody");
const productWorkshopsTableBody = document.querySelector("#product-workshops-table tbody");
const productWorkshopsSelect = document.getElementById("product-workshops-select");
const btnLoadProductWorkshops = document.getElementById("btn-load-product-workshops");
const productWorkshopsTime = document.getElementById("product-workshops-time");

const rawForm = document.getElementById("raw-form");
const rawResult = document.getElementById("raw-result");

function showPage(pageName) {
    Object.values(pages).forEach(page => page.classList.remove("visible"));
    Object.values(navButtons).forEach(btn => btn.classList.remove("active"));
    
    if (pages[pageName]) pages[pageName].classList.add("visible");
    if (navButtons[pageName]) navButtons[pageName].classList.add("active");
}

navButtons.products.addEventListener("click", () => showPage("products"));
navButtons.productTypes.addEventListener("click", () => {
    showPage("productTypes");
    loadProductTypes();
});
navButtons.materials.addEventListener("click", () => {
    showPage("materials");
    loadMaterials();
});
navButtons.workshops.addEventListener("click", () => {
    showPage("workshops");
    loadWorkshops();
});
navButtons.productWorkshops.addEventListener("click", () => {
    showPage("productWorkshops");
    loadProductsForSelect(productWorkshopsSelect);
});
navButtons.calc.addEventListener("click", () => showPage("calc"));

function showMessage(element, text, type = "info") {
    element.textContent = text;
    element.classList.remove("hidden", "error", "info");
    element.classList.add(type);
}

function hideMessage(element) {
    element.classList.add("hidden");
}

async function loadProductTypes() {
    productTypesTableBody.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/all-product-types`);
        if (!res.ok) throw new Error("Не удалось загрузить типы продукции");
        const data = await res.json();
        if (data.length === 0) {
            productTypesTableBody.innerHTML = "<tr><td colspan='2' style='text-align:center'>Нет данных</td></tr>";
            return;
        }
        data.forEach(t => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${t.product_type_name}</td>
                <td>${t.type_coefficient}</td>
            `;
            productTypesTableBody.appendChild(tr);
        });
    } catch (e) {
        productTypesTableBody.innerHTML = `<tr><td colspan='2' style='text-align:center;color:red'>Ошибка: ${e.message}</td></tr>`;
    }
}

async function loadMaterials() {
    materialsTableBody.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/all-materials`);
        if (!res.ok) throw new Error("Не удалось загрузить материалы");
        const data = await res.json();
        if (data.length === 0) {
            materialsTableBody.innerHTML = "<tr><td colspan='2' style='text-align:center'>Нет данных</td></tr>";
            return;
        }
        data.forEach(m => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${m.material_name}</td>
                <td>${m.loss_percentage}%</td>
            `;
            materialsTableBody.appendChild(tr);
        });
    } catch (e) {
        materialsTableBody.innerHTML = `<tr><td colspan='2' style='text-align:center;color:red'>Ошибка: ${e.message}</td></tr>`;
    }
}

async function loadWorkshops() {
    workshopsTableBody.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/all-workshops`);
        if (!res.ok) throw new Error("Не удалось загрузить цеха");
        const data = await res.json();
        if (data.length === 0) {
            workshopsTableBody.innerHTML = "<tr><td colspan='3' style='text-align:center'>Нет данных</td></tr>";
            return;
        }
        data.forEach(w => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${w.workshop_name}</td>
                <td>${w.workshop_type}</td>
                <td>${w.num_employees}</td>
            `;
            workshopsTableBody.appendChild(tr);
        });
    } catch (e) {
        workshopsTableBody.innerHTML = `<tr><td colspan='3' style='text-align:center;color:red'>Ошибка: ${e.message}</td></tr>`;
    }
}

async function loadProductsForSelect(selectElement) {
    selectElement.innerHTML = '<option value="">-- Выберите продукт --</option>';
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (!res.ok) return;
        const data = await res.json();
        data.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.product_id;
            opt.textContent = `${p.product_id} - ${p.product_name}`;
            selectElement.appendChild(opt);
        });
    } catch (e) {
        console.error("Ошибка загрузки продуктов:", e);
    }
}

btnLoadProductWorkshops.addEventListener("click", async () => {
    productWorkshopsTableBody.innerHTML = "";
    productWorkshopsTime.textContent = "";
    const productId = Number(productWorkshopsSelect.value);
    if (!productId || productId <= 0) {
        productWorkshopsTime.textContent = "Выберите продукт из списка.";
        productWorkshopsTime.classList.add("error");
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/product-workshops/${productId}`);
        if (!res.ok) throw new Error("Не удалось загрузить данные");
        const data = await res.json();
        
        if (data.length === 0) {
            productWorkshopsTableBody.innerHTML = "<tr><td colspan='3' style='text-align:center'>Нет данных</td></tr>";
            return;
        }
        
        data.forEach(pw => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${pw.product_name}</td>
                <td>${pw.workshop_name}</td>
                <td>${pw.coefficient} ч</td>
            `;
            productWorkshopsTableBody.appendChild(tr);
        });
        
        const timeRes = await fetch(`${API_BASE}/products/${productId}/production_time`);
        if (timeRes.ok) {
            const timeData = await timeRes.json();
            productWorkshopsTime.innerHTML = `<strong>Общее время изготовления: ${timeData.total_production_time} ч</strong>`;
            productWorkshopsTime.classList.remove("error");
        }
    } catch (e) {
        productWorkshopsTime.textContent = `Ошибка: ${e.message}`;
        productWorkshopsTime.classList.add("error");
    }
});

async function loadProductTypesForSelect(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">-- Выберите --</option>';
    const res = await fetch(`${API_BASE}/product-types`);
    if (!res.ok) return;
    const data = await res.json();
    data.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.product_type_name;
        opt.textContent = t.product_type_name;
        select.appendChild(opt);
    });
}

async function loadMaterialsForSelect(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">-- Выберите --</option>';
    const res = await fetch(`${API_BASE}/materials`);
    if (!res.ok) return;
    const data = await res.json();
    data.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.material_name;
        opt.textContent = m.material_name;
        select.appendChild(opt);
    });
}

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
                    <button class="secondary btn-edit" data-id="${p.product_id}" title="Редактировать">✏️</button>
                    <button class="secondary btn-delete" data-id="${p.product_id}" title="Удалить">🗑️</button>
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
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
}

btnAdd.addEventListener("click", () => {
    formTitle.textContent = "Добавить продукт";
    productForm.reset();
    document.getElementById("product_id").value = "";
    loadProductTypesForSelect("product_type_name");
    loadMaterialsForSelect("main_material_name");
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
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (!res.ok) throw new Error("Не удалось получить данные продукта");
        const data = await res.json();
        const p = data.find((x) => x.product_id === Number(id));
        if (!p) throw new Error("Продукт не найден");

        formTitle.textContent = "Редактировать продукт";
        document.getElementById("product_id").value = p.product_id;
        document.getElementById("product_name").value = p.product_name;
        document.getElementById("article").value = p.article;
        document.getElementById("min_partner_cost").value = p.min_partner_cost;
        
        await loadProductTypesForSelect("product_type_name");
        await loadMaterialsForSelect("main_material_name");
        
        if (p.product_type_name) {
            document.getElementById("product_type_name").value = p.product_type_name;
        }
        if (p.main_material_name) {
            document.getElementById("main_material_name").value = p.main_material_name;
        }

        modal.classList.remove("hidden");
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
}

productForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessage(messageBox);

    const id = document.getElementById("product_id").value;
    const payload = {
        product_name: document.getElementById("product_name").value.trim(),
        article: Number(document.getElementById("article").value),
        min_partner_cost: parseFloat(document.getElementById("min_partner_cost").value),
        product_type_name: document.getElementById("product_type_name").value.trim() || null,
        main_material_name: document.getElementById("main_material_name").value.trim() || null,
    };

    if (!payload.product_name || payload.article < 0 || payload.min_partner_cost < 0) {
        showMessage(messageBox, "Проверьте корректность данных в форме.", "error");
        return;
    }

    try {
        const url = id ? `${API_BASE}/products/${id}` : `${API_BASE}/products`;
        const method = id ? "PUT" : "POST";
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Ошибка сохранения продукта");
        }

        modal.classList.add("hidden");
        await loadProducts();
        showMessage(messageBox, "Данные успешно сохранены.", "info");
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
});

async function deleteProduct(id) {
    if (!confirm("Удалить этот продукт?")) return;
    try {
        const res = await fetch(`${API_BASE}/products/${id}`, { method: "DELETE" });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Ошибка удаления продукта");
        }
        await loadProducts();
        showMessage(messageBox, "Продукт удалён.", "info");
    } catch (e) {
        showMessage(messageBox, e.message, "error");
    }
}

rawForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    rawResult.textContent = "";
    rawResult.classList.remove("error", "info");

    const payload = {
        product_type_name: document.getElementById("raw_product_type_name").value.trim(),
        material_name: document.getElementById("raw_material_name").value.trim(),
        quantity: Number(document.getElementById("raw_quantity").value),
        param1: Number(document.getElementById("raw_param1").value),
        param2: Number(document.getElementById("raw_param2").value),
    };

    if (!payload.product_type_name || !payload.material_name || payload.quantity < 0 || payload.param1 <= 0 || payload.param2 <= 0) {
        rawResult.textContent = "Проверьте корректность введённых данных.";
        rawResult.classList.add("error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/calculate_raw_material`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) throw new Error("Ошибка расчёта сырья");

        const data = await res.json();
        if (data.required_raw_material === -1) {
            rawResult.textContent = "Ошибка: тип продукции или материал не найдены, либо указаны неверные параметры.";
            rawResult.classList.add("error");
        } else {
            rawResult.textContent = `Необходимое количество сырья: ${data.required_raw_material} единиц`;
            rawResult.classList.add("info");
        }
    } catch (e) {
        rawResult.textContent = `Ошибка: ${e.message}`;
        rawResult.classList.add("error");
    }
});

loadProducts();
loadProductTypesForSelect("raw_product_type_name");
loadMaterialsForSelect("raw_material_name");
loadProductsForSelect(productWorkshopsSelect);
