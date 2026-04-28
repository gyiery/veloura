document.addEventListener("DOMContentLoaded", function () {
    const userIcon = document.getElementById("userIcon");
    const loginModal = document.getElementById("loginModal");
    const registerModal = document.getElementById("registerModal");

    const openRegister = document.getElementById("openRegister");
    const openLogin = document.getElementById("openLogin");

    const closeLogin = document.getElementById("closeLogin");
    const closeRegister = document.getElementById("closeRegister");

    const accountIconWrap = document.getElementById("accountIconWrap");
    const accountModal = document.getElementById("accountModal");
    const closeAccount = document.getElementById("closeAccount");

    const accountDropdown = document.getElementById("accountDropdown");
    const openAccountModalBtn = document.getElementById("openAccountModalBtn");

    const arrivalsSlider = document.getElementById("arrivalsSlider");
    const arrivalsPrev = document.getElementById("arrivalsPrev");
    const arrivalsNext = document.getElementById("arrivalsNext");

    if (arrivalsSlider && arrivalsPrev && arrivalsNext) {
        arrivalsNext.addEventListener("click", function () {
            arrivalsSlider.scrollBy({
                left: 344,
                behavior: "smooth"
            });
        });

        arrivalsPrev.addEventListener("click", function () {
            arrivalsSlider.scrollBy({
                left: -344,
                behavior: "smooth"
            });
        });
    }

    if (userIcon && loginModal) {
        userIcon.addEventListener("click", function () {
            loginModal.style.display = "flex";
            registerModal && (registerModal.style.display = "none");
        });
    }

    if (openRegister && loginModal && registerModal) {
        openRegister.addEventListener("click", function () {
            loginModal.style.display = "none";
            registerModal.style.display = "flex";
        });
    }

    if (openLogin && loginModal && registerModal) {
        openLogin.addEventListener("click", function () {
            registerModal.style.display = "none";
            loginModal.style.display = "flex";
        });
    }

    if (closeLogin && loginModal) {
        closeLogin.addEventListener("click", function () {
            loginModal.style.display = "none";
        });
    }

    if (closeRegister && registerModal) {
        closeRegister.addEventListener("click", function () {
            registerModal.style.display = "none";
        });
    }

    if (accountIconWrap && accountDropdown) {
        accountIconWrap.addEventListener("click", function (e) {
            e.stopPropagation();
            accountDropdown.classList.toggle("show");
        });
    }

    if (openAccountModalBtn && accountModal && accountDropdown) {
        openAccountModalBtn.addEventListener("click", function () {
            accountDropdown.classList.remove("show");
            accountModal.style.display = "flex";
        });
    }

    if (closeAccount && accountModal) {
        closeAccount.addEventListener("click", function () {
            accountModal.style.display = "none";
        });
    }

    window.addEventListener("click", function (e) {
        if (e.target === loginModal) {
            loginModal.style.display = "none";
        }

        if (e.target === registerModal) {
            registerModal.style.display = "none";
        }

        if (e.target === accountModal) {
            accountModal.style.display = "none";
        }

        if (e.target === quickViewModal) {
        quickViewModal.style.display = "none";
        }

        if (accountDropdown && !accountDropdown.contains(e.target) && accountIconWrap && !accountIconWrap.contains(e.target)) {
            accountDropdown.classList.remove("show");
        }
    });

    const params = new URLSearchParams(window.location.search);
    const modal = params.get("modal");

    if (modal === "login" && loginModal) {
        loginModal.style.display = "flex";
    }

    if (modal === "register" && registerModal) {
        registerModal.style.display = "flex";
    }

    if (modal === "account" && accountModal) {
        accountModal.style.display = "flex";
    }

    setTimeout(function () {
        const messages = document.querySelectorAll(".site-message");
        messages.forEach(function (msg) {
            msg.style.opacity = "0";
            msg.style.transform = "translateX(40px)";
            msg.style.transition = "0.4s";
            setTimeout(function () {
                msg.remove();
            }, 400);
        });
    }, 3200);
});

    const quickViewModal = document.getElementById("quickViewModal");
    const closeQuickView = document.getElementById("closeQuickView");
    const quickViewButtons = document.querySelectorAll(".quick-view-btn");

    const quickViewImg = document.getElementById("quickViewImg");
    const quickViewTitle = document.getElementById("quickViewTitle");
    const quickViewCategory = document.getElementById("quickViewCategory");
    const quickViewPrice = document.getElementById("quickViewPrice");
    const quickViewDescription = document.getElementById("quickViewDescription");

    quickViewButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const title = button.getAttribute("data-title");
            const category = button.getAttribute("data-category");
            const price = button.getAttribute("data-price");
            const image = button.getAttribute("data-image");
            const description = button.getAttribute("data-description");

            if (quickViewTitle) quickViewTitle.textContent = title;
            if (quickViewCategory) quickViewCategory.textContent = category;
            if (quickViewPrice) quickViewPrice.textContent = price;
            if (quickViewDescription) quickViewDescription.textContent = description;
            if (quickViewImg) quickViewImg.src = image;

            if (quickViewModal) {
                quickViewModal.style.display = "flex";
            }
        });
    });

    if (closeQuickView && quickViewModal) {
        closeQuickView.addEventListener("click", function () {
            quickViewModal.style.display = "none";
        });
    }

        const paramsCart = new URLSearchParams(window.location.search);
    const added = paramsCart.get("added");

    if (added === "1") {
        const cartBadge = document.querySelector(".cart-badge");
        const allCartIcons = document.querySelectorAll(".cart-icon-wrap");

        allCartIcons.forEach(function (icon) {
            icon.classList.add("cart-bounce");
            setTimeout(function () {
                icon.classList.remove("cart-bounce");
            }, 700);
        });
    }

    const quickViewCartForm = document.getElementById("quickViewCartForm");
    const quickViewButtonsAll = document.querySelectorAll(".quick-view-btn");

    quickViewButtonsAll.forEach(function (button) {
        button.addEventListener("click", function () {
            const productId = button.closest(".best-card").getAttribute("data-product-id");
            if (quickViewCartForm && productId) {
                quickViewCartForm.action = `/add-to-cart/${productId}/`;
            }
        });
    });

window.addEventListener("load", function () {
    const preloader = document.getElementById("preloader");

    setTimeout(function () {
        preloader.classList.add("hide");
    }, 1200);
});


const promoSlides = document.querySelectorAll(".promo-slide");
const promoDots = document.querySelectorAll(".promo-dot");
const promoPrev = document.getElementById("promoPrev");
const promoNext = document.getElementById("promoNext");

let promoIndex = 0;
let promoInterval;

function showPromoSlide(index) {
    promoSlides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
    });

    promoDots.forEach((dot, i) => {
        dot.classList.toggle("active", i === index);
    });

    promoIndex = index;
}

function nextPromoSlide() {
    let nextIndex = (promoIndex + 1) % promoSlides.length;
    showPromoSlide(nextIndex);
}

function prevPromoSlide() {
    let prevIndex = (promoIndex - 1 + promoSlides.length) % promoSlides.length;
    showPromoSlide(prevIndex);
}

function startPromoSlider() {
    promoInterval = setInterval(nextPromoSlide, 5000);
}

function resetPromoSlider() {
    clearInterval(promoInterval);
    startPromoSlider();
}

if (promoSlides.length > 0) {
    promoNext.addEventListener("click", () => {
        nextPromoSlide();
        resetPromoSlider();
    });

    promoPrev.addEventListener("click", () => {
        prevPromoSlide();
        resetPromoSlider();
    });

    promoDots.forEach((dot) => {
        dot.addEventListener("click", () => {
            const slideIndex = parseInt(dot.getAttribute("data-slide"));
            showPromoSlide(slideIndex);
            resetPromoSlider();
        });
    });

    showPromoSlide(0);
    startPromoSlider();
}


document.addEventListener("DOMContentLoaded", function () {
    const chatToggleBtn = document.getElementById("chatToggleBtn");
    const chatCloseBtn = document.getElementById("chatCloseBtn");
    const chatPanel = document.getElementById("chatPanel");
    const startChatBtn = document.getElementById("startChatBtn");
    const chatUserForm = document.getElementById("chatUserForm");
    const chatConversation = document.getElementById("chatConversation");
    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendChatBtn = document.getElementById("sendChatBtn");
    const voiceChatBtn = document.getElementById("voiceChatBtn");

    let chatUserNameValue = "";
    let chatUserEmailValue = "";

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function scrollChatToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendMessage(sender, text) {
        if (!chatMessages) return;

        const messageDiv = document.createElement("div");
        messageDiv.className = sender === "user" ? "user-message" : "bot-message";
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        scrollChatToBottom();
    }

    function appendTypingBubble() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "bot-message typing-message";
        typingDiv.innerHTML = "<span></span><span></span><span></span>";
        chatMessages.appendChild(typingDiv);
        scrollChatToBottom();
        return typingDiv;
    }

    function removeTypingBubble(typingDiv) {
        if (typingDiv && typingDiv.parentNode) {
            typingDiv.parentNode.removeChild(typingDiv);
        }
    }

    function appendButtons(buttons) {
        if (!chatMessages || !buttons || !buttons.length) return;

        const container = document.createElement("div");
        container.className = "chat-suggestion-wrap";

        buttons.forEach((buttonText) => {
            const btn = document.createElement("button");
            btn.className = "chat-suggestion-btn";
            btn.type = "button";
            btn.textContent = buttonText;
            btn.addEventListener("click", function () {
                sendChatMessage(buttonText);
            });
            container.appendChild(btn);
        });

        chatMessages.appendChild(container);
        scrollChatToBottom();
    }

    function appendProducts(products) {
        if (!chatMessages || !products || !products.length) return;

        const grid = document.createElement("div");
        grid.className = "chat-product-grid";

        products.forEach((product) => {
            const card = document.createElement("div");
            card.className = "chat-product-card";

            const imageHtml = product.image
                ? `<img src="${product.image}" alt="${product.name}">`
                : `<div class="chat-product-placeholder">Veloura</div>`;

            card.innerHTML = `
                <div class="chat-product-image">
                    ${imageHtml}
                </div>
                <div class="chat-product-info">
                    <h4>${product.name}</h4>
                    <p>₹${product.price}</p>
                    <a href="${product.url}" class="chat-product-link">View Product</a>
                </div>
            `;

            grid.appendChild(card);
        });

        chatMessages.appendChild(grid);
        scrollChatToBottom();
    }

    async function sendChatMessage(customText = null) {
        if (!chatInput && !customText) return;

        const message = customText || chatInput.value.trim();
        if (!message) return;

        appendMessage("user", message);

        if (!customText) {
            chatInput.value = "";
        }

        const typingDiv = appendTypingBubble();

        try {
            const response = await fetch("/chatbot/ask/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    message: message,
                    name: chatUserNameValue,
                    email: chatUserEmailValue,
                }),
            });

            const data = await response.json();
            removeTypingBubble(typingDiv);

            appendMessage("bot", data.reply || "Sorry, I could not answer that.");
            appendButtons(data.buttons || []);
            appendProducts(data.products || []);
        } catch (error) {
            removeTypingBubble(typingDiv);
            appendMessage("bot", "Sorry, I’m unable to respond right now. Please try again.");
        }
    }

    if (chatToggleBtn && chatPanel) {
        chatToggleBtn.addEventListener("click", function () {
            chatPanel.classList.toggle("active");
        });
    }

    if (chatCloseBtn && chatPanel) {
        chatCloseBtn.addEventListener("click", function () {
            chatPanel.classList.remove("active");
        });
    }

    if (startChatBtn && chatUserForm && chatConversation) {
        startChatBtn.addEventListener("click", function () {
            const nameInput = document.getElementById("chatUserName");
            const emailInput = document.getElementById("chatUserEmail");

            const name = nameInput ? nameInput.value.trim() : "";
            const email = emailInput ? emailInput.value.trim() : "";

            if (!name || !email) {
                alert("Please fill your name and email.");
                return;
            }

            chatUserNameValue = name;
            chatUserEmailValue = email;

            chatUserForm.classList.add("hidden");
            chatConversation.classList.remove("hidden");

            appendMessage("bot", `Welcome ${name} ✨ How may I help you with Veloura today?`);
            appendButtons(["Show Products", "Best Products", "New Arrivals", "Perfumes"]);
        });
    }

    if (sendChatBtn) {
        sendChatBtn.addEventListener("click", function () {
            sendChatMessage();
        });
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                sendChatMessage();
            }
        });
    }

    // Voice input
    if (voiceChatBtn) {
        voiceChatBtn.addEventListener("click", function () {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                alert("Voice input is not supported in this browser.");
                return;
            }

            const recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            voiceChatBtn.disabled = true;
            voiceChatBtn.textContent = "🎙️";

            recognition.start();

            recognition.onresult = function (event) {
                const transcript = event.results[0][0].transcript;
                if (chatInput) {
                    chatInput.value = transcript;
                }
            };

            recognition.onerror = function () {
                alert("Voice input could not be captured. Please try again.");
            };

            recognition.onend = function () {
                voiceChatBtn.disabled = false;
                voiceChatBtn.textContent = "🎤";
            };
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const qtyMinusBtn = document.getElementById("qtyMinusBtn");
    const qtyPlusBtn = document.getElementById("qtyPlusBtn");
    const qtyValue = document.getElementById("qtyValue");
    const cartQuantityInput = document.getElementById("cartQuantityInput");
    const buyNowQuantityInput = document.getElementById("buyNowQuantityInput");

    const pincodeInput = document.getElementById("pincodeInput");
    const checkPincodeBtn = document.getElementById("checkPincodeBtn");
    const pincodeResult = document.getElementById("pincodeResult");

    const shareProductBtn = document.getElementById("shareProductBtn");

    if (qtyMinusBtn && qtyPlusBtn && qtyValue) {
        let quantity = 1;

        function updateQuantity() {
            qtyValue.textContent = quantity;

            if (cartQuantityInput) {
                cartQuantityInput.value = quantity;
            }

            if (buyNowQuantityInput) {
                buyNowQuantityInput.value = quantity;
            }
        }

        qtyMinusBtn.addEventListener("click", function () {
            if (quantity > 1) {
                quantity--;
                updateQuantity();
            }
        });

        qtyPlusBtn.addEventListener("click", function () {
            quantity++;
            updateQuantity();
        });

        updateQuantity();
    }

    if (checkPincodeBtn && pincodeInput && pincodeResult) {
        checkPincodeBtn.addEventListener("click", async function () {
            const pincode = pincodeInput.value.trim();

            if (!pincode) {
                pincodeResult.textContent = "Please enter a pincode.";
                return;
            }

            try {
                const response = await fetch(`/check-pincode/?pincode=${encodeURIComponent(pincode)}`);
                const data = await response.json();

                pincodeResult.textContent = data.message;
                pincodeResult.style.color = data.success ? "#0d6b2f" : "#b00020";
            } catch (error) {
                pincodeResult.textContent = "Could not check pincode right now. Please try again.";
                pincodeResult.style.color = "#b00020";
            }
        });
    }

    if (shareProductBtn) {
        shareProductBtn.addEventListener("click", async function () {
            const shareData = {
                title: document.title,
                text: "Check out this product on Veloura",
                url: window.location.href
            };

            try {
                if (navigator.share) {
                    await navigator.share(shareData);
                } else {
                    await navigator.clipboard.writeText(window.location.href);
                    alert("Product link copied successfully.");
                }
            } catch (error) {
                console.log("Share cancelled or failed.");
            }
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("search-input");
    const resultsBox = document.getElementById("search-results");
    const hiddenInput = document.getElementById("hidden-search-input");
    const form = document.getElementById("search-form");
    const clearBtn = document.getElementById("search-clear");

    if (!input || !resultsBox || !hiddenInput || !form || !clearBtn) return;

    function toggleClearButton() {
        if (input.value.trim().length > 0) {
            clearBtn.classList.add("show");
        } else {
            clearBtn.classList.remove("show");
        }
    }

    // LIVE SEARCH
    input.addEventListener("keyup", function () {
        let query = input.value.trim();
        hiddenInput.value = query;

        toggleClearButton();

        if (query.length < 1) {
            resultsBox.innerHTML = "";
            return;
        }

        fetch(`/live-search/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                let html = "";

                if (data.results.length > 0) {
                    data.results.forEach(product => {
                        html += `
                            <div class="search-item" onclick="window.location='/product/${product.id}/'">
                                <img src="${product.image}" alt="${product.name}">
                                <div>
                                    <p>${product.name}</p>
                                    <span>₹${product.price}</span>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = `<p class="no-result">No products found</p>`;
                }

                resultsBox.innerHTML = html;
            });
    });

    // ENTER → SEARCH PAGE
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            form.submit();
        }
    });

    // CLEAR BUTTON
    clearBtn.addEventListener("click", function () {
        input.value = "";
        hiddenInput.value = "";
        resultsBox.innerHTML = "";
        clearBtn.classList.remove("show");
        input.focus();
    });

    // CLICK OUTSIDE → CLOSE DROPDOWN
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".search-box")) {
            resultsBox.innerHTML = "";
        }
    });
});