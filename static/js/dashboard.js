<script>
    var ctxRevenue = document.getElementById('revenueChart').getContext('2d');
    var revenueChart = new Chart(ctxRevenue, {
        type: 'bar',
        data: {
            labels: ['January', 'February', 'March'],
            datasets: [{
                label: 'Total Revenue',
                data: [12000, 19000, 3000],
                backgroundColor: '#E1001A',
            }]
        },
    });

    var ctxSales = document.getElementById('salesChart').getContext('2d');
    var salesChart = new Chart(ctxSales, {
        type: 'pie',
        data: {
            labels: ['Product A', 'Product B', 'Product C'],
            datasets: [{
                label: 'Monthly Sales',
                data: [1000, 2000, 3000],
                backgroundColor: ['#00478F', '#E1001A', '#5A5A5A'],
            }]
        },
    });
</script>
