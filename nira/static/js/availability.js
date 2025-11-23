(() => {
    const cardsWrap = document.getElementById("availability-cards");
    const hiddenInput = document.getElementById("visit_date");
    const selectedLabel = document.getElementById("selected-date-label");
    const refreshBtn = document.getElementById("refresh-availability");
    const submitBtn = document.getElementById("book-button");

    const dailyLimit = window.dailyLimit || 20;
    const initialAvailability = Array.isArray(window.initialAvailability)
        ? window.initialAvailability
        : [];

    const locale = window.localeText || {};
    const monthShort = new Intl.DateTimeFormat(undefined, { month: "short" });
    const longDate = new Intl.DateTimeFormat(undefined, {
        month: "long",
        day: "numeric",
        year: "numeric",
    });

    const toDate = (value) => new Date(`${value}T12:00:00`);

    let currentAvailability = initialAvailability;
    let selectedDate = hiddenInput?.value || null;

    const setSelected = (dateStr) => {
        selectedDate = dateStr;
        if (hiddenInput) hiddenInput.value = dateStr || "";
        if (submitBtn) submitBtn.disabled = !dateStr;

        if (!selectedLabel) return;
        if (!dateStr) {
            selectedLabel.textContent = locale.noDates || "No dates open right now.";
            return;
        }
        const dateObj = toDate(dateStr);
        selectedLabel.textContent = `${locale.selectedDate || "Selected: "} ${longDate.format(dateObj)}`;
    };

    const renderCards = () => {
        if (!cardsWrap) return;
        cardsWrap.innerHTML = "";

        if (!currentAvailability.length) {
            const empty = document.createElement("p");
            empty.className = "empty-state";
            empty.textContent = locale.noDates || `All dates in the current window are booked (limit ${dailyLimit} per day). Please check again soon.`;
            cardsWrap.appendChild(empty);
            setSelected(null);
            return;
        }

        // Default select first available if none chosen
        const selectable = currentAvailability.filter((d) => d.remaining > 0).map((d) => d.date);
        if (!selectedDate || (selectedDate && !selectable.includes(selectedDate))) {
            setSelected(selectable[0] || null);
        } else {
            setSelected(selectedDate);
        }

        const buildCard = (slot, interactive = true) => {
            const dateObj = toDate(slot.date);
            const card = document.createElement("div");
            card.className = "availability-card";
            if (slot.date === selectedDate && interactive) {
                card.classList.add("selected");
            }
            if (slot.remaining === 0) {
                card.classList.add("disabled");
            }
            const dateBlock = document.createElement("div");
            dateBlock.className = "date-block";
            const monthEl = document.createElement("span");
            monthEl.className = "month";
            monthEl.textContent = monthShort.format(dateObj);
            const dayEl = document.createElement("span");
            dayEl.className = "day";
            dayEl.textContent = dateObj.getDate().toString().padStart(2, "0");
            dateBlock.appendChild(monthEl);
            dateBlock.appendChild(dayEl);

            const meta = document.createElement("div");
            meta.className = "availability-meta";
            const spotsEl = document.createElement("span");
            spotsEl.className = "spots";
            const suffix = locale.spotsSuffix || "spots left";
            spotsEl.textContent = slot.remaining === 0
                ? (locale.fullLabel || "Full")
                : `${slot.remaining} ${suffix}`;
            meta.appendChild(spotsEl);

            card.appendChild(dateBlock);
            card.appendChild(meta);

            if (interactive && slot.remaining > 0) {
                card.addEventListener("click", () => {
                    selectedDate = slot.date;
                    setSelected(slot.date);
                    renderCards();
                });
            } else {
                card.classList.add("compact");
            }

            return card;
        };

        currentAvailability.forEach((slot) => {
            cardsWrap.appendChild(buildCard(slot, true));
        });
    };

    const renderAvailability = (availability) => {
        currentAvailability = availability || [];
        renderCards();
    };

    renderAvailability(initialAvailability);

    const refreshAvailability = async () => {
        try {
            const response = await fetch("/availability");
            if (!response.ok) return;
            const data = await response.json();
            renderAvailability(data.available_dates || []);
        } catch (error) {
            console.error("Availability refresh failed", error);
        }
    };

    if (refreshBtn) {
        refreshBtn.addEventListener("click", (e) => {
            e.preventDefault();
            refreshAvailability();
        });
    }
})();
