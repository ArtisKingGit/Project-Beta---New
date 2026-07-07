import { ref, get } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-database.js";

export const applyTheme = (theme) => {
    document.body.classList.remove('light-theme', 'dark-theme');
    document.documentElement.classList.remove('light-theme', 'dark-theme');
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        document.documentElement.classList.add('light-theme');
    } else if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.documentElement.classList.add('dark-theme');
    } else {
        // System Default
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const targetTheme = prefersDark ? 'dark-theme' : 'light-theme';
        document.body.classList.add(targetTheme);
        document.documentElement.classList.add(targetTheme);
    }
    // Cache for early-load script
    localStorage.setItem('agrofast-theme', theme || 'dark');
};

export const formatPrice = (priceInKES, currency = 'KES') => {
    const rates = {
        'KES': { rate: 1, symbol: 'KSh' },
        'USD': { rate: 0.0077, symbol: '$' },
        'UGX': { rate: 28, symbol: 'USh' },
        'TZS': { rate: 20, symbol: 'TSh' },
        'ZAR': { rate: 0.14, symbol: 'R' }
    };

    const config = rates[currency] || rates['KES'];
    const converted = priceInKES * config.rate;

    return `${config.symbol} ${converted.toLocaleString(undefined, { maximumFractionDigits: (currency === 'USD' || currency === 'ZAR' ? 2 : 0) })}`;
};

export const initTheme = async (db, user) => {
    try {
        const snapshot = await get(ref(db, `users/${user.uid}/settings`));
        const settings = snapshot.val();
        if (settings && settings.theme) {
            applyTheme(settings.theme);
        } else {
            // Default to dark or system
            const cached = localStorage.getItem('agrofast-theme') || 'dark';
            applyTheme(cached);
        }
    } catch (e) {
        console.error("Error initializing theme:", e);
        const cached = localStorage.getItem('agrofast-theme') || 'dark';
        applyTheme(cached);
    }
};
