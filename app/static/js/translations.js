/* Dynamic Kannada & English Translation System for Saree Factory Portal */
const TRANSLATIONS = {
    en: {
        // Navigation & Sidebar
        "Dashboard": "Dashboard",
        "Saree Catalog": "Saree Catalog",
        "Worker Registry": "Worker Registry",
        "Daily Production": "Daily Production",
        "Billing & PDF": "Billing & PDF",
        "Wholesale Buyers": "Wholesale Buyers",
        "Sales Invoices": "Sales Invoices",
        "Activity Logs": "Activity Logs",
        "Sign Out": "Sign Out",
        
        // Admin Dashboard
        "Admin Dashboard": "Admin Dashboard",
        "Real-time production monitoring & analytics": "Real-time production monitoring & analytics",
        "Total Production": "Total Production",
        "Worker Payments": "Worker Payments",
        "Total Revenue": "Total Revenue",
        "Net Profit": "Net Profit",
        "Sarees woven globally": "Sarees woven globally",
        "Total labor cost paid": "Total labor cost paid",
        "Wholesale values": "Wholesale values",
        "Net earnings margin": "Net earnings margin",
        "Recent Production Logs": "Recent Production Logs",
        "Production & Profit Trend (Last 15 Days)": "Production & Profit Trend (Last 15 Days)",
        "Category Popularity": "Category Popularity",
        "Top 5 Active Weavers (By Volume & Payouts)": "Top 5 Active Weavers (By Volume & Payouts)",

        // Saree Catalog
        "Saree Catalog & Pricing": "Saree Catalog & Pricing",
        "Manage saree designs, wholesale rates, and weaver payments": "Manage saree designs, wholesale rates, and weaver payments",
        "Add New Saree": "Add New Saree",
        "Saree Name": "Saree Name",
        "Category": "Category",
        "Cost Price": "Cost Price",
        "Selling Price": "Selling Price",
        "Worker Payment": "Worker Payment",
        "Actions": "Actions",
        "Edit Saree": "Edit Saree",
        "Delete": "Delete",

        // Worker Registry
        "Weaver & Worker Registry": "Weaver & Worker Registry",
        "Manage loom workers, contact details, and advance payouts": "Manage loom workers, contact details, and advance payouts",
        "Add New Weaver": "Add New Weaver",
        "Name": "Name",
        "Phone": "Phone",
        "Address": "Address",
        "Joining Date": "Joining Date",
        "Status": "Status",
        "Active": "Active",
        "Inactive": "Inactive",
        "Issue Advance Payout": "Issue Advance Payout",
        "Advance History": "Advance History",

        // Daily Production
        "Daily Production Ledger": "Daily Production Ledger",
        "Track daily saree weaving records and worker earnings": "Track daily saree weaving records and worker earnings",
        "Record Daily Work": "Record Daily Work",
        "Select Weaver": "Select Weaver",
        "Select Saree": "Select Saree",
        "Quantity": "Quantity",
        "Date": "Date",
        "Weaver Earnings": "Weaver Earnings",
        "Company Revenue": "Company Revenue",

        // Billing
        "Weaver Billing & Settlements": "Weaver Billing & Settlements",
        "Generate weekly payout statements and track advance deductions": "Generate weekly payout statements and track advance deductions",
        "Generate Statement": "Generate Statement",
        "Statement Period": "Statement Period",
        "Unbilled Advances": "Unbilled Advances",
        "Net Payout": "Net Payout",
        "Compile Report & PDF": "Compile Report & PDF",

        // Customers & Invoices
        "Wholesale Buyers Registry": "Wholesale Buyers Registry",
        "Manage customer accounts, GSTIN, and location details": "Manage customer accounts, GSTIN, and location details",
        "Add New Buyer": "Add New Buyer",
        "GSTIN": "GSTIN",
        "State Code": "State Code",
        "Sales Invoices (Outside Parties)": "Sales Invoices (Outside Parties)",
        "Track wholesale saree shipments, transport documentation, tax charges, and print official invoices": "Track wholesale saree shipments, transport documentation, tax charges, and print official invoices",
        "Generate Sales Invoice": "Generate Sales Invoice",
        "Print Bill": "Print Bill",

        // Worker Portal
        "Weaver Portal": "Weaver Portal",
        "Track your daily production history, earnings, and settled bills": "Track your daily production history, earnings, and settled bills",
        "Woven Today": "Woven Today",
        "This Week Earnings": "This Week Earnings",
        "This Month Earnings": "This Month Earnings",
        "Unsettled Balance": "Unsettled Balance",
        "Submit Today's Work": "Submit Today's Work"
    },
    kn: {
        // Navigation & Sidebar
        "Dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "Saree Catalog": "ಸೀರೆ ಕ್ಯಾಟಲಾಗ್",
        "Worker Registry": "ನೇಯ್ಗೆಗಾರರ ನೋಂದಣಿ",
        "Daily Production": "ದಿನನಿತ್ಯದ ಉತ್ಪಾದನೆ",
        "Billing & PDF": "ಬಿಲ್ಲಿಂಗ್ & ಪಿಡಿಎಫ್",
        "Wholesale Buyers": "ಸಗಟು ಗ್ರಾಹಕರು",
        "Sales Invoices": "ಮಾರಾಟದ ಸರಕುಪಟ್ಟಿ",
        "Activity Logs": "ಚಟುವಟಿಕೆ ಲಾಗ್‌ಗಳು",
        "Sign Out": "ನಿರ್ಗಮಿಸಿ",
        
        // Admin Dashboard
        "Admin Dashboard": "ನಿರ್ವಾಹಕ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "Real-time production monitoring & analytics": "ನೈಜ ಸಮಯದ ಉತ್ಪಾದನಾ ಮೇಲ್ವಿಚಾರಣೆ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ",
        "Total Production": "ಒಟ್ಟು ಉತ್ಪಾದನೆ",
        "Worker Payments": "ನೇಯ್ಗೆಗಾರರ ಪಾವತಿಗಳು",
        "Total Revenue": "ಒಟ್ಟು ಆದಾಯ",
        "Net Profit": "ನಿವ್ವಳ ಲಾಭ",
        "Sarees woven globally": "ಒಟ್ಟು ನೇಯ್ದ ಸೀರೆಗಳು",
        "Total labor cost paid": "ಪಾವತಿಸಿದ ಒಟ್ಟು ಕೂಲಿ ವೆಚ್ಚ",
        "Wholesale values": "ಸಗಟು ಮೌಲ್ಯಗಳು",
        "Net earnings margin": "ನಿವ್ವಳ ಆದಾಯದ ಮಾರ್ಜಿನ್",
        "Recent Production Logs": "ಇತ್ತೀಚಿನ ಉತ್ಪಾದನಾ ಲಾಗ್‌ಗಳು",
        "Production & Profit Trend (Last 15 Days)": "ಉತ್ಪಾದನೆ ಮತ್ತು ಲಾಭದ ಟ್ರೆಂಡ್ (ಕೊನೆಯ 15 ದಿನಗಳು)",
        "Category Popularity": "ವರ್ಗಗಳ ಜನಪ್ರಿಯತೆ",
        "Top 5 Active Weavers (By Volume & Payouts)": "ಟಾಪ್ 5 ಸಕ್ರಿಯ ನೇಯ್ಗೆಗಾರರು",

        // Saree Catalog
        "Saree Catalog & Pricing": "ಸೀರೆ ಕ್ಯಾಟಲಾಗ್ ಮತ್ತು ಬೆಲೆಗಳು",
        "Manage saree designs, wholesale rates, and weaver payments": "ಸೀರೆ ವಿನ್ಯಾಸಗಳು, ಸಗಟು ದರಗಳು ಮತ್ತು ಕೂಲಿ ನಿರ್ವಹಿಸಿ",
        "Add New Saree": "ಹೊಸ ಸೀರೆ ಸೇರಿಸಿ",
        "Saree Name": "ಸೀರೆಯ ಹೆಸರು",
        "Category": "ವರ್ಗ",
        "Cost Price": "ವೆಚ್ಚದ ಬೆಲೆ",
        "Selling Price": "ಮಾರಾಟದ ಬೆಲೆ",
        "Worker Payment": "ನೇಯ್ಗೆಗಾರರ ಕೂಲಿ",
        "Actions": "ಕ್ರಿಯೆಗಳು",
        "Edit Saree": "ಸೀರೆ ತಿದ್ದುಪಡಿ",
        "Delete": "ಅಳಿಸಿ",

        // Worker Registry
        "Weaver & Worker Registry": "ನೇಯ್ಗೆಗಾರರ ನೋಂದಣಿ ಪುಸ್ತಕ",
        "Manage loom workers, contact details, and advance payouts": "ನೇಯ್ಗೆಗಾರರು, ಸಂಪರ್ಕ ವಿವರಗಳು ಮತ್ತು ಮುಂಗಡ ಪಾವತಿ ನಿರ್ವಹಿಸಿ",
        "Add New Weaver": "ಹೊಸ ನೇಯ್ಗೆಗಾರರನ್ನು ಸೇರಿಸಿ",
        "Name": "ಹೆಸರು",
        "Phone": "ದೂರವಾಣಿ",
        "Address": "ವಿಳಾಸ",
        "Joining Date": "ಸೇರ್ಪಡೆ ದಿನಾಂಕ",
        "Status": "ಸ್ಥಿತಿ",
        "Active": "ಸಕ್ರಿಯ",
        "Inactive": "ನಿಷ್ಕ್ರಿಯ",
        "Issue Advance Payout": "ಮುಂಗಡ ಹಣ ನೀಡಿ",
        "Advance History": "ಮುಂಗಡ ಇತಿಹಾಸ",

        // Daily Production
        "Daily Production Ledger": "ದಿನನಿತ್ಯದ ಉತ್ಪಾದನಾ ಲೆಡ್ಜರ್",
        "Track daily saree weaving records and worker earnings": "ದಿನನಿತ್ಯದ ಸೀರೆ ನೇಯ್ಗೆ ಮತ್ತು ಕೂಲಿ ದಾಖಲಿಸಿ",
        "Record Daily Work": "ದಿನದ ಕೆಲಸವನ್ನು ನಮೂದಿಸಿ",
        "Select Weaver": "ನೇಯ್ಗೆಗಾರರನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
        "Select Saree": "ಸೀರೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
        "Quantity": "ಪ್ರಮಾಣ",
        "Date": "ದಿನಾಂಕ",
        "Weaver Earnings": "ನೇಯ್ಗೆಗಾರರ ಗಳಿಕೆ",
        "Company Revenue": "ಸಂಸ್ಥೆಯ ಆದಾಯ",

        // Billing
        "Weaver Billing & Settlements": "ನೇಯ್ಗೆಗಾರರ ಬಿಲ್ಲಿಂಗ್ & ಇತ್ಯರ್ಥಗಳು",
        "Generate weekly payout statements and track advance deductions": "ವಾರದ ಬಿಲ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್ ತಯಾರಿಸಿ ಮತ್ತು ಮುಂಗಡ ಕಡಿತ ಪರಿಶೀಲಿಸಿ",
        "Generate Statement": "ಸ್ಟೇಟ್‌ಮೆಂಟ್ ತಯಾರಿಸಿ",
        "Statement Period": "ಸ್ಟೇಟ್‌ಮೆಂಟ್ ಅವಧಿ",
        "Unbilled Advances": "ಬಾಕಿ ಮುಂಗಡ",
        "Net Payout": "ನಿವ್ವಳ ಪಾವತಿ",
        "Compile Report & PDF": "ವರದಿ ಮತ್ತು ಪಿಡಿಎಫ್ ತಯಾರಿಸಿ",

        // Customers & Invoices
        "Wholesale Buyers Registry": "ಸಗಟು ಖರೀದಿದಾರರ ನೋಂದಣಿ",
        "Manage customer accounts, GSTIN, and location details": "ಗ್ರಾಹಕರ ಖಾತೆಗಳು, ಜಿಎಸ್‌ಟಿ ಸಂಖ್ಯೆ ಮತ್ತು ವಿಳಾಸ ನಿರ್ವಹಿಸಿ",
        "Add New Buyer": "ಹೊಸ ಖರೀದಿದಾರರನ್ನು ಸೇರಿಸಿ",
        "GSTIN": "ಜಿಎಸ್‌ಟಿ ಸಂಖ್ಯೆ",
        "State Code": "ರಾಜ್ಯ ಕೋಡ್",
        "Sales Invoices (Outside Parties)": "ಮಾರಾಟದ ಸರಕುಪಟ್ಟಿಗಳು",
        "Track wholesale saree shipments, transport documentation, tax charges, and print official invoices": "ಸಗಟು ಸೀರೆ ರವಾನೆ, ಸಾರಿಗೆ ದಾಖಲೆಗಳು, ತೆರಿಗೆ ಬಿಲ್ ನಿರ್ವಹಿಸಿ ಮತ್ತು ಬಿಲ್ಲು ಮುದ್ರಿಸಿ",
        "Generate Sales Invoice": "ಹೊಸ ಮಾರಾಟ ಸರಕುಪಟ್ಟಿ ರಚಿಸಿ",
        "Print Bill": "ಬಿಲ್ಲು ಮುದ್ರಿಸಿ",

        // Worker Portal
        "Weaver Portal": "ನೇಯ್ಗೆಗಾರರ ಪೋರ್ಟಲ್",
        "Track your daily production history, earnings, and settled bills": "ನಿಮ್ಮ ದಿನನಿತ್ಯದ ಉತ್ಪಾದನೆ, ಗಳಿಕೆ ಮತ್ತು ಬಿಲ್ ಪರಿಶೀಲಿಸಿ",
        "Woven Today": "ಇಂದು ನೇಯ್ದದ್ದು",
        "This Week Earnings": "ಈ ವಾರದ ಗಳಿಕೆ",
        "This Month Earnings": "ಈ ತಿಂಗಳ ಗಳಿಕೆ",
        "Unsettled Balance": "ಬಾಕಿ ಪಾವತಿ",
        "Submit Today's Work": "ಇಂದಿನ ಕೆಲಸವನ್ನು ಸಲ್ಲಿಸಿ"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const langToggleBtn = document.getElementById('lang-toggle');
    const langLabel = document.getElementById('lang-label');
    
    // Check saved language preference (default: English)
    let currentLang = localStorage.getItem('saree-factory-lang') || 'en';
    
    // Apply language on initial load
    applyLanguage(currentLang);
    
    if (langToggleBtn) {
        langToggleBtn.addEventListener('click', () => {
            currentLang = (currentLang === 'en') ? 'kn' : 'en';
            localStorage.setItem('saree-factory-lang', currentLang);
            applyLanguage(currentLang);
        });
    }
    
    function applyLanguage(lang) {
        document.documentElement.lang = lang;
        if (langLabel) {
            langLabel.textContent = (lang === 'en') ? 'ಕನ್ನಡ' : 'English';
        }
        
        // Translate text nodes across all key components
        translateElements(lang);
    }
    
    function translateElements(lang) {
        // Skip automatic text translation on login page to preserve form button formatting
        if (document.querySelector('.login-card')) return;
        
        const dictionary = TRANSLATIONS[lang];
        if (!dictionary) return;
        
        const selectors = [
            '.nav-item a > span',
            '.nav-section-title',
            '.page-title h1',
            '.page-title p',
            '.stat-title',
            '.stat-card p',
            '.widget-title',
            '.custom-table th',
            '.form-group label',
            '.badge',
            '.username-label',
            '.role-badge'
        ];
        
        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => translateSingleElement(el, dictionary, lang));
        });
        
        // Handle buttons without child spans
        document.querySelectorAll('.btn').forEach(btn => {
            if (btn.querySelector('span')) return; // child span handled above
            translateSingleElement(btn, dictionary, lang);
        });
    }
    
    function translateSingleElement(el, dictionary, lang) {
        if (!el.getAttribute('data-original-text')) {
            let text = getDirectText(el).trim();
            if (text) {
                el.setAttribute('data-original-text', text);
            }
        }
        
        const originalText = el.getAttribute('data-original-text');
        if (originalText && dictionary[originalText]) {
            setDirectText(el, dictionary[originalText]);
        } else if (lang === 'en' && originalText) {
            setDirectText(el, originalText);
        }
    }
    
    function getDirectText(element) {
        let text = '';
        element.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
                text += node.textContent;
            }
        });
        return text;
    }
    
    function setDirectText(element, newText) {
        let textNodes = [];
        element.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0) {
                textNodes.push(node);
            }
        });
        
        if (textNodes.length > 0) {
            textNodes[0].textContent = ' ' + newText + ' ';
            for (let i = 1; i < textNodes.length; i++) {
                textNodes[i].textContent = '';
            }
        }
    }
});
