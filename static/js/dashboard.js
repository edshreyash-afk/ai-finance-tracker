// AI Finance Tracker - Dashboard & Utilities
// Core chart rendering + app-wide utilities

let charts = {};  // Chart cache
let filteredData = [];  // For client-side filtering

/**
 * Your renderChart function - Enhanced
 */
function renderChart(graphData, elementId) {
    if (!graphData) {
        console.warn('No graph data for', elementId);
        return;
    }
    
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Element not found:', elementId);
        return;
    }
    
    try {
        Plotly.newPlot(element, graphData.data, graphData.layout || {}, {
            responsive: true,
            displayModeBar: false,
            showTips: false,
            displaylogo: false
        });
        charts[elementId] = graphData;  // Cache for resize/update
        console.log(`✅ Chart rendered: ₹{elementId}`);
    } catch (error) {
        console.error('Plotly render error:', error);
        element.innerHTML = '<div class="text-center py-4 text-muted"><i class="bi bi-graph-down"></i> Chart unavailable</div>';
    }
}

/**
 * Password visibility toggle (login/register)
 */
function initPasswordToggle() {
    document.querySelectorAll('#togglePassword').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const inputGroup = toggle.closest('.input-group');
            const password = inputGroup?.querySelector('input[type="password"]') || 
                           document.querySelector('input[name="password"]');
            const icon = toggle.querySelector('i');
            
            if (password) {
                password.type = password.type === 'password' ? 'text' : 'password';
                icon.classList.toggle('bi-eye');
                icon.classList.toggle('bi-eye-slash');
            }
        });
    });
}

/**
 * Real-time password confirmation (register.html)
 */
function initPasswordMatch() {
    const pass1 = document.querySelector('input[name="password"]');
    const pass2 = document.querySelector('input[name="password_confirm"]');
    
    if (!pass1 || !pass2) return;
    
    function checkMatch() {
        if (pass1.value && pass2.value && pass1.value !== pass2.value) {
            pass2.classList.add('is-invalid');
            pass2.classList.remove('is-valid');
        } else if (pass2.value) {
            pass2.classList.remove('is-invalid');
            pass2.classList.add('is-valid');
        }
    }
    
    pass1.addEventListener('input', checkMatch);
    pass2.addEventListener('input', checkMatch);
}

/**
 * Table search & filter (transactions.html)
 */
function initTableSearch(tableSelector = '.table') {
    const searchInput = document.querySelector('#searchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', debounce((e) => {
        const term = e.target.value.toLowerCase();
        const rows = document.querySelectorAll(`₹{tableSelector} tbody tr`);
        
        let visibleCount = 0;
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(term)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        updateCounter(visibleCount);
    }, 250));
}

function updateCounter(count) {
    const counter = document.querySelector('.transaction-counter');
    if (counter) counter.textContent = `Found ₹{count} transactions`;
}

/**
 * CSV Export utility
 */
function exportTransactionsCSV() {
    const rows = document.querySelectorAll('.table tbody tr[style=""]');  // Visible rows
    const data = [];
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            data.push({
                date: cells[1]?.textContent.trim(),
                description: cells[2]?.textContent.trim(),
                category: cells[3]?.textContent.trim(),
                amount: cells[4]?.textContent.trim(),
                type: cells[5]?.textContent.trim()
            });
        }
    });
    
    if (data.length) {
        const csv = convertToCSV(data);
        downloadCSV(csv, 'transactions.csv');
    }
}

function convertToCSV(data) {
    const headers = ['Date', 'Description', 'Category', 'Amount', 'Type'];
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            `"₹{row.date}"`, `"₹{row.description}"`, 
            `"₹{row.category}"`, `"₹{row.amount}"`, `"₹{row.type}"`
        ].join(','))
    ].join('\n');
    return csvContent;
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Select all checkboxes
 */
function initSelectAll() {
    const selectAll = document.querySelector('#selectAll');
    if (!selectAll) return;
    
    selectAll.addEventListener('change', (e) => {
        document.querySelectorAll('.transaction-checkbox').forEach(cb => {
            cb.checked = e.target.checked;
        });
        toggleBulkActions();
    });
    
    document.querySelectorAll('.transaction-checkbox').forEach(cb => {
        cb.addEventListener('change', toggleBulkActions);
    });
}

function toggleBulkActions() {
    const checked = document.querySelectorAll('.transaction-checkbox:checked').length;
    const deleteBtn = document.querySelector('#deleteSelected');
    if (deleteBtn) {
        deleteBtn.disabled = checked === 0;
        deleteBtn.textContent = checked ? `Delete ₹{checked}` : 'Delete Selected';
    }
}

/**
 * Debounce utility
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Auto-initialize everything
 */
document.addEventListener('DOMContentLoaded', function() {
    // Init all features
    initPasswordToggle();
    initPasswordMatch();
    initTableSearch();
    initSelectAll();
    
    // Export buttons
    document.querySelector('#exportCSV')?.addEventListener('click', exportTransactionsCSV);
    
    console.log('🚀 Dashboard JS fully loaded - All features active');
});

// Export utilities globally
window.renderChart = renderChart;
window.exportTransactionsCSV = exportTransactionsCSV;
window.initTableSearch = initTableSearch;
