document.addEventListener('DOMContentLoaded', function() {
    // Kalkulacija ukupne garancije
    function updateTotalGuarantee() {
        const guaranteeFields = [
            'id_seriousness_guarantee_percentage',
            'id_performance_guarantee_percentage',
            'id_warranty_guarantee_percentage'
        ];
        
        const total = guaranteeFields.reduce((sum, fieldId) => {
            const field = document.getElementById(fieldId);
            return sum + (parseFloat(field?.value) || 0);
        }, 0);

        const totalElement = document.getElementById('total_guarantee');
        if (totalElement) {
            totalElement.textContent = `${total.toFixed(2)}%`;
        }
    }

    // Event listeners za garancije
    document.querySelectorAll([
        '#id_seriousness_guarantee_percentage',
        '#id_performance_guarantee_percentage',
        '#id_warranty_guarantee_percentage'
    ].join(',')).forEach(field => {
        field?.addEventListener('input', updateTotalGuarantee);
    });

    // Inicijalno ažuriranje
    updateTotalGuarantee();

    // Formset handling
    const formsetHandlers = {
        dokumentacije: {
            addBtn: 'add-dokumentacija',
            removeClass: 'remove-dokumentacija',
            container: 'dokumentacije_formset'
        }
    };

    // Initialize formset handlers
    Object.entries(formsetHandlers).forEach(([prefix, config]) => {
        initializeFormsetHandler(prefix, config);
    });
});

// Formset initialization helper
function initializeFormsetHandler(prefix, config) {
    const addButton = document.getElementById(config.addBtn);
    const container = document.getElementById(config.container);

    if (addButton && container) {
        addButton.addEventListener('click', (e) => {
            e.preventDefault();
            addFormsetForm(prefix, container);
        });

        // Delegation for remove buttons
        container.addEventListener('click', (e) => {
            if (e.target.classList.contains(config.removeClass)) {
                e.preventDefault();
                removeFormsetForm(e.target.closest(`.${prefix}-form`), prefix);
            }
        });
    }
}

// Additional helper functions will go here...
