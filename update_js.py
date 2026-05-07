import os

js_code = """
// =========================================================================
// 7. EVENT FILTERING — Events Section
// =========================================================================

let currentEventFilter = 'all';

function filterEvents(filterVal = null, btn = null) {
    if (filterVal !== null) {
        currentEventFilter = filterVal;
    }
    
    // Update active state on buttons if btn is provided
    if (btn) {
        const buttons = document.querySelectorAll('.event-filter-btn');
        buttons.forEach(b => {
            // Remove active classes
            b.classList.remove('bg-slate-800', 'text-white', 'border-slate-600');
            b.classList.add('bg-transparent', 'text-slate-400', 'border-transparent');
        });
        
        // Add active classes to clicked button
        btn.classList.remove('bg-transparent', 'text-slate-400', 'border-transparent');
        btn.classList.add('bg-slate-800', 'text-white', 'border-slate-600');
    }

    const searchQuery = (document.getElementById('eventSearchInput')?.value || '').toLowerCase();
    const cards = document.querySelectorAll('.event-card');

    cards.forEach(card => {
        const type = card.dataset.type || '';
        const status = card.dataset.status || '';
        const title = card.dataset.title || '';
        
        let showByType = false;
        
        if (currentEventFilter === 'all') {
            showByType = true;
        } else if (currentEventFilter.startsWith('status:')) {
            showByType = status === currentEventFilter.split(':')[1];
        } else {
            showByType = type === currentEventFilter;
        }

        const showBySearch = title.includes(searchQuery);

        if (showByType && showBySearch) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}
"""

with open('s:/CECP/static/js/main.js', 'a', encoding='utf-8') as f:
    f.write(js_code)
