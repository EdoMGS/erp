document.addEventListener('DOMContentLoaded', function() {
    const calculatorForm = document.getElementById('calculatorForm');
    
    if (calculatorForm) {
        calculatorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('totalCost').textContent = 
                        new Intl.NumberFormat('hr-HR', {
                            style: 'currency',
                            currency: 'EUR'
                        }).format(data.total_cost);
                        
                    document.getElementById('margin').textContent = 
                        `${parseFloat(data.margin).toFixed(2)}%`;
                        
                    // Update chart
                    updateCostBreakdown();
                }
            });
        });
    }
    
    // Initialize supplier price fetching
    initializeSupplierPrices();
});

function initializeSupplierPrices() {
    document.querySelectorAll('.supplier-select').forEach(select => {
        select.addEventListener('change', function() {
            const endpoint = this.dataset.endpoint;
            const item = new URLSearchParams(endpoint).get('item');
            
            fetch(endpoint)
                .then(response => response.json())
                .then(data => {
                    const priceInput = this.closest('.pricing')
                        .querySelector('.price-input');
                    priceInput.value = data.prices[this.value] || '';
                    updateCalculations();
                });
        });
    });
}

function updateCostBreakdown() {
    const ctx = document.getElementById('costBreakdown').getContext('2d');
    // Update chart logic here
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
