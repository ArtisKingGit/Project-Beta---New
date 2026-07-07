import { getDatabase, ref, update, get } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-database.js";
import { applyTranslations, translations } from "./translations.js";
import { applyTheme } from "./theme.js";

export async function checkTutorial(user, db) {
    const snap = await get(ref(db, `users/${user.uid}/tutorialSeen`));
    if (!snap.exists() || !snap.val()) {
        window.startTutorial(true);
    }
}

export async function checkRecTutorial(user, db) {
    const snap = await get(ref(db, `users/${user.uid}/recTutorialSeen`));
    if (!snap.exists() || !snap.val()) {
        window.startRecommendationsTutorial();
    }
}

window.startTutorial = (isNew = false) => {
    let selectedLang = localStorage.getItem('agrofast-lang') || 'en';
    let selectedTheme = localStorage.getItem('agrofast-theme') || 'dark';
    
    let currentStep = 0;
    if (localStorage.getItem('agrofast-lang')) {
        currentStep = 1;
    }
    if (localStorage.getItem('agrofast-lang') && localStorage.getItem('agrofast-theme')) {
        currentStep = 2;
    }

    const overlay = document.createElement('div');
    overlay.className = 'tutorial-overlay';
    overlay.id = 'tutorialOverlay';

    const spotlight = document.createElement('div');
    spotlight.className = 'tutorial-spotlight';
    spotlight.id = 'tutorialSpotlight';
    spotlight.style.display = 'none';

    const renderStep = () => {
        const t = translations[selectedLang];
        let content = '';
        let highlightSelector = '';
        let cardPosition = 'center';

        // Step 0: Language
        if (currentStep === 0) {
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-seedling"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.welcome}</h2>
                    <p class="tutorial-desc">${t.tutorial.welcome_desc}</p>
                    <div class="tutorial-lang-select" style="grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));">
                        <div class="lang-card ${selectedLang === 'en' ? 'active' : ''}" onclick="window.setTutorialLang('en')" style="padding: 12px 6px;">
                            <span style="font-size: 20px; display: block;">🇺🇸</span>
                            <strong style="font-size: 13px;">English</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'sw' ? 'active' : ''}" onclick="window.setTutorialLang('sw')" style="padding: 12px 6px;">
                            <span style="font-size: 20px; display: block;">🇰🇪</span>
                            <strong style="font-size: 13px;">Kiswahili</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'zu' ? 'active' : ''}" onclick="window.setTutorialLang('zu')" style="padding: 12px 6px;">
                            <span style="font-size: 20px; display: block;">🇿🇦</span>
                            <strong style="font-size: 13px;">isiZulu</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 've' ? 'active' : ''}" onclick="window.setTutorialLang('ve')" style="padding: 12px 6px;">
                            <span style="font-size: 20px; display: block;">🇿🇦</span>
                            <strong style="font-size: 13px;">Tshivenda</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'af' ? 'active' : ''}" onclick="window.setTutorialLang('af')" style="padding: 12px 6px;">
                            <span style="font-size: 20px; display: block;">🇿🇦</span>
                            <strong style="font-size: 13px;">Afrikaans</strong>
                        </div>
                    </div>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 1: Theme
        else if (currentStep === 1) {
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-palette"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.theme_title}</h2>
                    <p class="tutorial-desc">${t.tutorial.theme_desc}</p>
                    <div class="theme-selection">
                        <div class="theme-card light ${selectedTheme === 'light' ? 'active' : ''}" onclick="window.setTutorialTheme('light')">
                            <i class="fas fa-sun"></i>
                            <strong>${t.tutorial.light_mode}</strong>
                        </div>
                        <div class="theme-card dark ${selectedTheme === 'dark' ? 'active' : ''}" onclick="window.setTutorialTheme('dark')">
                            <i class="fas fa-moon"></i>
                            <strong>${t.tutorial.dark_mode}</strong>
                        </div>
                    </div>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 2: Sidebar Tour
        else if (currentStep === 2) {
            highlightSelector = '.sidebar';
            cardPosition = 'right';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-bars"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.step1_title}</h2>
                    <p class="tutorial-desc">${t.tutorial.step1_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 3: Scanner Tour
        else if (currentStep === 3) {
            highlightSelector = '.scanner-widget';
            cardPosition = 'bottom';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-camera"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_scanner}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_scanner_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 4: Weather Tour
        else if (currentStep === 4) {
            highlightSelector = '.weather-widget';
            cardPosition = 'bottom';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-cloud-sun"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_weather}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_weather_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 5: Budget Widget Tour
        else if (currentStep === 5) {
            highlightSelector = '.budget-widget';
            cardPosition = 'bottom';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-piggy-bank"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_budget}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_budget_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 6: Quick Actions Tour
        else if (currentStep === 6) {
            highlightSelector = '.quick-actions-widget';
            cardPosition = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-bolt"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_actions}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_actions_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 7: Inventory Tour
        else if (currentStep === 7) {
            highlightSelector = '.inventory-widget';
            cardPosition = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-boxes"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_inventory}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_inventory_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        }
        // Step 8: AI Assistant Tour (Finish)
        else if (currentStep === 8) {
            highlightSelector = '#aiToggleBtn';
            cardPosition = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-robot"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_assistant || 'AgroFast AI Assistant'}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_assistant_desc || 'Need instant crop or financial advice? Chat with our AI assistant here at any time.'}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.finishTutorial(${isNew})">${t.tutorial.finish}</button>
                    </div>
                </div>
            `;
        }

        overlay.innerHTML = content;
        updateSpotlight(highlightSelector, cardPosition);
    };

    const updateSpotlight = (selector, cardPos) => {
        const target = selector ? document.querySelector(selector) : null;
        const card = overlay.querySelector('.tutorial-card');

        if (target) {
            const rect = target.getBoundingClientRect();
            spotlight.style.display = 'block';
            spotlight.style.top = (rect.top - 10) + 'px';
            spotlight.style.left = (rect.left - 10) + 'px';
            spotlight.style.width = (rect.width + 20) + 'px';
            spotlight.style.height = (rect.height + 20) + 'px';
            overlay.classList.add('transparent');

            if (window.innerWidth >= 768) {
                card.style.position = 'fixed';
                card.style.top = '';
                card.style.bottom = '';
                card.style.left = '';
                card.style.right = '';
                card.style.transform = '';

                const cardH = 320; // estimated card height
                const margin = 20;
                const vw = window.innerWidth;
                const vh = window.innerHeight;

                // Horizontal: centre, clamped
                const clampedLeft = Math.min(Math.max((vw / 2), 270), vw - 270);

                if (cardPos === 'right') {
                    const leftPos = rect.right + 40;
                    card.style.left = (leftPos + 520 > vw ? rect.left - 560 : leftPos) + 'px';
                    card.style.top = '50%';
                    card.style.transform = 'translateY(-50%)';
                } else if (cardPos === 'bottom' || (cardPos === 'top' && rect.top < cardH + margin)) {
                    // Place below if enough room, or target is too high for above placement
                    let topPos = rect.bottom + margin;
                    if (topPos + cardH > vh) topPos = vh - cardH - margin;
                    if (topPos < 0) topPos = margin;
                    card.style.top = topPos + 'px';
                    card.style.left = clampedLeft + 'px';
                    card.style.transform = 'translateX(-50%)';
                } else if (cardPos === 'top') {
                    let topPos = rect.top - cardH - margin;
                    if (topPos < margin) topPos = rect.bottom + margin;
                    if (topPos + cardH > vh) topPos = vh - cardH - margin;
                    card.style.top = Math.max(margin, topPos) + 'px';
                    card.style.left = clampedLeft + 'px';
                    card.style.transform = 'translateX(-50%)';
                }
            } else {
                card.style.position = 'relative';
                card.style.top = 'auto';
                card.style.left = 'auto';
                card.style.bottom = 'auto';
                card.style.right = 'auto';
                card.style.transform = 'none';
            }
        } else {
            spotlight.style.display = 'none';
            overlay.classList.remove('transparent');
            card.style.position = 'relative';
            card.style.top = 'auto';
            card.style.left = 'auto';
            card.style.bottom = 'auto';
            card.style.right = 'auto';
            card.style.transform = 'none';
        }
    };

    window.setTutorialLang = (lang) => {
        selectedLang = lang;
        applyTranslations(lang);
        renderStep();
    };

    window.setTutorialTheme = (theme) => {
        selectedTheme = theme;
        applyTheme(theme);
        renderStep();
    };

    window.nextTutorialStep = () => {
        currentStep++;
        renderStep();
    };

    window.finishTutorial = async (isNewUser) => {
        try {
            const db = getDatabase();
            const user = window.firebaseUser;
            if (user) {
                const userRef = ref(db, `users/${user.uid}`);
                await update(userRef, { tutorialSeen: true });
                await update(ref(db, `users/${user.uid}/settings`), {
                    lang: selectedLang,
                    theme: selectedTheme
                });
            }
        } catch (err) {
            console.error("Tutorial Finish Error:", err);
        } finally {
            if (overlay) overlay.remove();
            if (spotlight) spotlight.remove();
            if (isNewUser) location.reload();
        }
    };

    document.body.appendChild(spotlight);
    document.body.appendChild(overlay);
    renderStep();
};

window.startRecommendationsTutorial = () => {
    let currentStep = 0;
    const lang = localStorage.getItem('agrofast-lang') || 'en';
    const t = translations[lang].rec_tutorial;

    const overlay = document.createElement('div');
    overlay.className = 'tutorial-overlay';

    const spotlight = document.createElement('div');
    spotlight.className = 'tutorial-spotlight';
    spotlight.style.display = 'none';

    const renderStep = () => {
        let content = '';
        let highlight = '';
        let pos = 'center';

        if (currentStep === 0) {
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-magic"></i></div>
                    <h2 class="tutorial-title">${t.welcome}</h2>
                    <p class="tutorial-desc">${t.welcome_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextRecStep()">${translations[lang].tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 1) {
            highlight = '.weather-banner';
            pos = 'bottom';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-cloud-sun"></i></div>
                    <h2 class="tutorial-title">${t.seasons}</h2>
                    <p class="tutorial-desc">${t.seasons_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextRecStep()">${translations[lang].tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 2) {
            highlight = '.controls-area';
            pos = 'bottom';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-filter"></i></div>
                    <h2 class="tutorial-title">${t.farms}</h2>
                    <p class="tutorial-desc">${t.farms_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextRecStep()">${translations[lang].tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 3) {
            highlight = '.crop-grid';
            pos = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-chart-line"></i></div>
                    <h2 class="tutorial-title">${t.prices}</h2>
                    <p class="tutorial-desc">${t.prices_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.finishRecTutorial()">${t.finish}</button>
                    </div>
                </div>
            `;
        }

        overlay.innerHTML = content;
        updateSpotlight(highlight, pos);
    };

    const updateSpotlight = (selector, cardPos) => {
        const target = selector ? document.querySelector(selector) : null;
        const card = overlay.querySelector('.tutorial-card');

        if (target) {
            const rect = target.getBoundingClientRect();
            spotlight.style.display = 'block';
            spotlight.style.top = (rect.top - 10) + 'px';
            spotlight.style.left = (rect.left - 10) + 'px';
            spotlight.style.width = (rect.width + 20) + 'px';
            spotlight.style.height = (rect.height + 20) + 'px';
            overlay.classList.add('transparent');

            card.style.position = 'fixed';
            if (cardPos === 'bottom') {
                card.style.top = (rect.bottom + 40) + 'px';
                card.style.left = '50%';
                card.style.transform = 'translateX(-50%)';
            } else if (cardPos === 'top') {
                card.style.bottom = (window.innerHeight - rect.top + 40) + 'px';
                card.style.left = '50%';
                card.style.transform = 'translateX(-50%)';
            }
        } else {
            spotlight.style.display = 'none';
            overlay.classList.remove('transparent');
            card.style.position = 'relative';
        }
    };

    window.nextRecStep = () => { currentStep++; renderStep(); };
    window.finishRecTutorial = async () => {
        const db = getDatabase();
        if (window.firebaseUser) {
            await update(ref(db, `users/${window.firebaseUser.uid}`), { recTutorialSeen: true });
        }
        overlay.remove();
        spotlight.remove();
    };

    document.body.appendChild(spotlight);
    document.body.appendChild(overlay);
    renderStep();
};

export function checkLoginTutorial() {
    const snap = localStorage.getItem('agrofast-login-tutorial-seen');
    if (!snap) {
        window.startLoginTutorial();
    }
}

window.startLoginTutorial = () => {
    let currentStep = 0;
    let selectedLang = localStorage.getItem('agrofast-lang') || 'en';

    const overlay = document.createElement('div');
    overlay.className = 'tutorial-overlay';
    overlay.id = 'loginTutorialOverlay';

    const spotlight = document.createElement('div');
    spotlight.className = 'tutorial-spotlight';
    spotlight.id = 'loginTutorialSpotlight';
    spotlight.style.display = 'none';

    const renderStep = () => {
        const t = translations[selectedLang] || translations.en;
        let content = '';
        let highlightSelector = '';
        let cardPosition = 'center';

        if (currentStep === 0) {
            highlightSelector = '';
            cardPosition = 'center';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-seedling"></i></div>
                    <h2 class="tutorial-title">${selectedLang === 'sw' ? 'Karibu AgroFast!' : selectedLang === 'zu' ? 'Siyakwamukela ku-AgroFast!' : selectedLang === 've' ? 'Wamukela kha AgroFast!' : selectedLang === 'af' ? 'Welkom by AgroFast!' : 'Welcome to AgroFast!'}</h2>
                    <p class="tutorial-desc">${selectedLang === 'sw' ? 'Kichanganuzi chako cha kidijitali cha kilimo. Hebu tukuonyeshe mfumo wetu mpya!' : selectedLang === 'zu' ? 'Isikena sakho sezitshalo zedijithali. Ake sikukhombise isistimu yethu entsha!' : selectedLang === 've' ? 'Tshisikeni tsha zwalwa tsha vhutali. Kha ri ni sumbedze programu yashu!' : selectedLang === 'af' ? 'U alles-in-een digitale landbou-toepassing. Kom ons wys u rond!' : 'Your all-in-one digital agriculture application. Let us show you around our interactive platform!'}</p>
                    <div class="tutorial-lang-select" style="grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); margin-bottom: 20px;">
                        <div class="lang-card ${selectedLang === 'en' ? 'active' : ''}" onclick="window.setLoginTutorialLang('en')" style="padding: 10px 5px;">
                            <span style="font-size: 18px; display: block;">🇺🇸</span>
                            <strong style="font-size: 12px;">English</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'sw' ? 'active' : ''}" onclick="window.setLoginTutorialLang('sw')" style="padding: 10px 5px;">
                            <span style="font-size: 18px; display: block;">🇰🇪</span>
                            <strong style="font-size: 12px;">Kiswahili</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'zu' ? 'active' : ''}" onclick="window.setLoginTutorialLang('zu')" style="padding: 10px 5px;">
                            <span style="font-size: 18px; display: block;">🇿🇦</span>
                            <strong style="font-size: 12px;">isiZulu</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 've' ? 'active' : ''}" onclick="window.setLoginTutorialLang('ve')" style="padding: 10px 5px;">
                            <span style="font-size: 18px; display: block;">🇿🇦</span>
                            <strong style="font-size: 12px;">Tshivenda</strong>
                        </div>
                        <div class="lang-card ${selectedLang === 'af' ? 'active' : ''}" onclick="window.setLoginTutorialLang('af')" style="padding: 10px 5px;">
                            <span style="font-size: 18px; display: block;">🇿🇦</span>
                            <strong style="font-size: 12px;">Afrikaans</strong>
                        </div>
                    </div>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextLoginTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 1) {
            highlightSelector = '.auth-container';
            cardPosition = 'left';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-user-lock"></i></div>
                    <h2 class="tutorial-title">${selectedLang === 'sw' ? 'Lango la Kuingia' : selectedLang === 'zu' ? 'Ingosi Yokungena' : selectedLang === 've' ? 'Lango la Akhaundu' : selectedLang === 'af' ? 'Toegangsportaal' : 'Access Portal'}</h2>
                    <p class="tutorial-desc">${selectedLang === 'sw' ? 'Jisajili au uingie ili kuhifadhi data ya shamba lako na kupata huduma zote.' : selectedLang === 'zu' ? 'Ngena noma ubhalise ukuze ugcine idatha yakho futhi ufinyelele zonke izici.' : selectedLang === 've' ? 'Dzhena kana u dzhie akhaundu u vhulaya datha ya mabulasi anu.' : selectedLang === 'af' ? 'Teken in of registreer om u plaasdata veilig te stoor en toegang tot ontledings te kry.' : 'Sign in to access your custom profile, or register to secure your farm data and access predictive analytics.'}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextLoginTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 2) {
            highlightSelector = '.features-grid';
            cardPosition = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-list-check"></i></div>
                    <h2 class="tutorial-title">${selectedLang === 'sw' ? 'Sifa Kuu' : selectedLang === 'zu' ? 'Izici Eziyinhloko' : selectedLang === 've' ? 'Zwithu zha Ndeme' : selectedLang === 'af' ? 'Kernkenmerke' : 'Core Capabilities'}</h2>
                    <p class="tutorial-desc">${selectedLang === 'sw' ? 'Chunguza sifa kuu: skana ya majani, mshauri wa AI, na udhibiti wa matumizi.' : selectedLang === 'zu' ? 'Hlola izici eziyinhloko: isikena sezitshalo, umsizi we-AI, nokuphathwa kwezimali.' : selectedLang === 've' ? 'Sedza zwithu zha ndeme: tshisikeni, mufuda we AI na u langula tshelede.' : selectedLang === 'af' ? 'Ontdek ons primêre gereedskap: die gewasskandeerder, AI-assistent en uitgawebestuurder.' : 'Discover our primary tools: AI Diagnostic Leaf Scanner, AgroFast AI advisor, and Farm Expense Manager.'}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.nextLoginTutorialStep()">${t.tutorial.next}</button>
                    </div>
                </div>
            `;
        } else if (currentStep === 3) {
            highlightSelector = '#aiToggleBtn';
            cardPosition = 'top';
            content = `
                <div class="tutorial-card">
                    <div class="tutorial-icon"><i class="fas fa-robot"></i></div>
                    <h2 class="tutorial-title">${t.tutorial.tour_assistant}</h2>
                    <p class="tutorial-desc">${t.tutorial.tour_assistant_desc}</p>
                    <div class="tutorial-btns">
                        <button class="btn-tutorial btn-next" onclick="window.finishLoginTutorial()">${t.tutorial.finish}</button>
                    </div>
                </div>
            `;
        }

        overlay.innerHTML = content;
        updateSpotlight(highlightSelector, cardPosition);
    };

    const updateSpotlight = (selector, cardPos) => {
        const target = selector ? document.querySelector(selector) : null;
        const card = overlay.querySelector('.tutorial-card');

        if (target) {
            const rect = target.getBoundingClientRect();
            spotlight.style.display = 'block';
            spotlight.style.top = (rect.top - 10) + 'px';
            spotlight.style.left = (rect.left - 10) + 'px';
            spotlight.style.width = (rect.width + 20) + 'px';
            spotlight.style.height = (rect.height + 20) + 'px';
            overlay.classList.add('transparent');

            if (window.innerWidth >= 768) {
                card.style.position = 'fixed';
                card.style.top = '';
                card.style.bottom = '';
                card.style.left = '';
                card.style.right = '';
                card.style.transform = '';

                const cardH = 300;
                const margin = 20;
                const vw = window.innerWidth;
                const vh = window.innerHeight;
                const clampedLeft = Math.min(Math.max((vw / 2), 270), vw - 270);

                if (cardPos === 'left') {
                    card.style.top = '50%';
                    const leftPos = rect.left - 520;
                    card.style.left = (leftPos > 10 ? leftPos : 10) + 'px';
                    card.style.transform = 'translateY(-50%)';
                } else if (cardPos === 'bottom' || (cardPos === 'top' && rect.top < cardH + margin)) {
                    let topPos = rect.bottom + margin;
                    if (topPos + cardH > vh) topPos = vh - cardH - margin;
                    if (topPos < 0) topPos = margin;
                    card.style.top = topPos + 'px';
                    card.style.left = clampedLeft + 'px';
                    card.style.transform = 'translateX(-50%)';
                } else if (cardPos === 'top') {
                    let topPos = rect.top - cardH - margin;
                    if (topPos < margin) topPos = rect.bottom + margin;
                    if (topPos + cardH > vh) topPos = vh - cardH - margin;
                    card.style.top = Math.max(margin, topPos) + 'px';
                    card.style.left = clampedLeft + 'px';
                    card.style.transform = 'translateX(-50%)';
                }
            } else {
                card.style.position = 'relative';
                card.style.top = 'auto';
                card.style.left = 'auto';
                card.style.bottom = 'auto';
                card.style.right = 'auto';
                card.style.transform = 'none';
            }
        } else {
            spotlight.style.display = 'none';
            overlay.classList.remove('transparent');
            card.style.position = 'relative';
            card.style.top = 'auto';
            card.style.left = 'auto';
            card.style.bottom = 'auto';
            card.style.right = 'auto';
            card.style.transform = 'none';
        }
    };

    window.setLoginTutorialLang = (lang) => {
        selectedLang = lang;
        localStorage.setItem('agrofast-lang', lang);
        renderStep();
    };

    window.nextLoginTutorialStep = () => {
        currentStep++;
        renderStep();
    };

    window.finishLoginTutorial = () => {
        localStorage.setItem('agrofast-login-tutorial-seen', 'true');
        overlay.remove();
        spotlight.remove();
    };

    document.body.appendChild(spotlight);
    document.body.appendChild(overlay);
    renderStep();
};
