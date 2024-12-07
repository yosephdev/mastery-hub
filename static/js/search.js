document.addEventListener('DOMContentLoaded', function() {    
    const filterForm = document.getElementById('filter-form');
    const searchForm = document.getElementById('search-form');

    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(filterForm);
            const searchParams = new URLSearchParams(formData);            
           
            const searchQuery = document.querySelector('input[name="q"]')?.value;
            if (searchQuery) {
                searchParams.set('q', searchQuery);
            }
            
            window.location.href = `${window.location.pathname}?${searchParams.toString()}`;
        });
    }
   
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const searchParams = new URLSearchParams(window.location.search);
                        
            for (const [key, value] of searchParams.entries()) {
                if (key !== 'q' && key !== 'page') {
                    formData.append(key, value);
                }
            }
            
            const newSearchParams = new URLSearchParams(formData);
            window.location.href = `${window.location.pathname}?${newSearchParams.toString()}`;
        });
    }
});
